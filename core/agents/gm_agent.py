"""
Game Master (GM) Agent - main dialogue agent.
Handles conversation with user and predictive quant requests.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.models import Quant

logger = logging.getLogger(__name__)


class GMAgent:
    """
    Game Master Agent - leads the dialogue and narrative.
    
    Responsibilities:
    - Generate response to user
    - Predict which quants will be needed for NEXT turn
    - Maintain style and narrative flow
    
    Does NOT:
    - Create or modify quants
    - Access full memory database
    - Make decisions about memory persistence
    """
    
    def __init__(self, llm_client: OpenRouterClient, model: Optional[str] = None):
        """Initialize GM agent."""
        self.llm = llm_client
        self.model = model  # Can override default model
    
    async def generate_response(
        self,
        context_messages: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response to user message.
        
        Args:
            context_messages: Pre-built context from ContextManager
            user_message: User's current message
            temperature: Sampling temperature
        
        Returns:
            Dict with:
            - reply: Text response to user
            - quants: List of quant names for next turn
            - raw_response: Full LLM response (for debugging)
        """
        # Add user message to context
        messages = context_messages + [
            {"role": "user", "content": user_message}
        ]
        
        try:
            # Call LLM with JSON mode for DeepSeek V3.2
            response = await self.llm.chat_completion(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Force JSON mode
            )
            
            # Extract content
            content = self.llm.extract_content(response)
            
            # Parse JSON response
            result = self._parse_gm_response(content)
            result["raw_response"] = content
            
            return result
        
        except Exception as e:
            logger.error(f"Error in GM agent: {e}")
            # Return fallback response
            return {
                "reply": "Произошла ошибка. Попробуй ещё раз.",
                "quants": [],
                "raw_response": str(e)
            }
    
    def _parse_gm_response(self, content: str) -> Dict[str, Any]:
        """
        Parse GM response into structured format.
        
        Expected format:
        ```json
        {
          "reply": "Text response",
          "quants": ["Quant1", "Quant2"]
        }
        ```
        """
        # Try direct JSON parse
        try:
            data = json.loads(content)
            return self._validate_gm_response(data)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code block
        if "```json" in content:
            try:
                json_str = content.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_str)
                return self._validate_gm_response(data)
            except (json.JSONDecodeError, IndexError):
                pass
        
        # Try extracting JSON object from text
        import re
        json_match = re.search(r'\{[^{}]*"reply"[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return self._validate_gm_response(data)
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to extract from various markdown/text formats
        logger.warning("Could not parse GM response as JSON, using text fallback")
        
        # Try to extract reply from **reply**: format
        reply = content
        quants = []
        
        # Pattern 1: **reply**: "text" **quants**: [...]
        if "**reply**:" in content and "**quants**:" in content:
            try:
                reply_part = content.split("**reply**:")[1].split("**quants**:")[0].strip()
                # Remove quotes
                reply = reply_part.strip().strip('"').strip("'")
                
                quants_part = content.split("**quants**:")[1].strip()
                # Extract quants from list format [A, B, C] or ["A", "B", "C"]
                import re
                quant_matches = re.findall(r'["\']([^"\']+)["\']', quants_part)
                if quant_matches:
                    quants = quant_matches
                else:
                    # Try without quotes
                    quant_matches = re.findall(r'[\[,]\s*([A-Za-zА-Яа-я_0-9]+)', quants_part)
                    quants = [q.strip() for q in quant_matches if q.strip()]
            except Exception as e:
                logger.warning(f"Failed to parse **reply**/**quants** format: {e}")
        
        # Pattern 2: "Запрошенные кванты:" markdown section
        if not quants and ("Запрошенные кванты:" in content or "**Запрошенные кванты:**" in content):
            # Find the quants section
            quants_section = content.split("Запрошенные кванты:")[-1].split("\n\n")[0]
            # Extract list items (lines starting with * or -)
            for line in quants_section.split("\n"):
                line = line.strip()
                if line.startswith("*") or line.startswith("-"):
                    quant = line.lstrip("*-").strip()
                    if quant:
                        quants.append(quant)
            
            # Extract reply (everything before "Запрошенные кванты:")
            if "**Запрошенные кванты:**" in content:
                reply = content.split("**Запрошенные кванты:**")[0].strip()
            elif "Запрошенные кванты:" in content:
                reply = content.split("Запрошенные кванты:")[0].strip()
        
        # Pattern 3: Extract from markers =Name= in text
        if not quants:
            import re
            # Find all =Name= markers
            marker_matches = re.findall(r'=([А-Яа-яA-Za-z0-9_]+)=', content)
            if marker_matches:
                # Deduplicate and add to quants
                quants = list(set(marker_matches))
                logger.info(f"Extracted {len(quants)} quants from markers: {quants}")
        
        # Pattern 4: Try to find JSON-like structure anywhere in text
        if not quants:
            import re
            # Look for "quants": [...] or 'quants': [...]
            quants_match = re.search(r'["\']quants["\']\s*:\s*\[([^\]]+)\]', content, re.IGNORECASE)
            if quants_match:
                quants_str = quants_match.group(1)
                # Extract quoted strings
                quant_matches = re.findall(r'["\']([^"\']+)["\']', quants_str)
                if quant_matches:
                    quants = quant_matches
                    logger.info(f"Extracted {len(quants)} quants from embedded JSON: {quants}")
        
        # Clean up reply
        if reply.startswith('**reply**:'):
            reply = reply.replace('**reply**:', '').strip().strip('"').strip("'")
        
        return {
            "reply": reply,
            "quants": quants
        }
    
    def _validate_gm_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize GM response."""
        if not isinstance(data, dict):
            raise ValueError("GM response must be a dict")
        
        # Ensure required fields
        if "reply" not in data:
            logger.warning("GM response missing 'reply' field")
            data["reply"] = str(data)
        
        if "quants" not in data:
            data["quants"] = []
        
        # Ensure quants is a list
        if not isinstance(data["quants"], list):
            data["quants"] = []
        
        # Validate quant names and clean markers
        import re
        cleaned_quants = []
        for q in data["quants"]:
            if q and str(q).strip():
                # Remove = markers if present (e.g. "=Name=" → "Name")
                cleaned = re.sub(r'^=+|=+$', '', str(q).strip())
                if cleaned:
                    cleaned_quants.append(cleaned)
        
        data["quants"] = cleaned_quants
        
        return data
    
    def extract_marked_entities(self, text: str, marker: str = "=") -> List[str]:
        """
        Extract entity names marked in text.
        
        Example: "Ты встречаешь =Маша= в =Таверна Атарикс="
        Returns: ["Маша", "Таверна Атарикс"]
        """
        import re
        pattern = f"{re.escape(marker)}([^{re.escape(marker)}]+){re.escape(marker)}"
        matches = re.findall(pattern, text)
        return [m.strip() for m in matches if m.strip()]

