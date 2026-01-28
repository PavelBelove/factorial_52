"""
Translator Agent - converts Russian turns to English structured JSON
"""
import json
import logging
from typing import Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.config import settings
from core.utils.agent_logger import log_agent_call

logger = logging.getLogger(__name__)


class TranslatorAgent:
    """
    Translates and compresses game turns from Russian to English JSON.
    
    Takes player action + GM response and converts to structured English format,
    removing unnecessary details and keeping essential narrative elements.
    """
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.model = "x-ai/grok-4.1-fast"  # Optimal: cheap + fast + good quality
    
    async def translate_turn(
        self,
        player_action: str,
        gm_response: str,
        turn_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Translate and compress one turn to English JSON-like text.
        
        NOTE: Returns RAW text in JSON-like format, NOT parsed JSON!
        LLM agents understand structured text even with syntax errors.
        This is for token efficiency, not for machine parsing.
        
        Args:
            player_action: Player's action in Russian
            gm_response: GM's response in Russian
            turn_number: Turn number
        
        Returns:
            Dict with 'content' (raw text) and 'cost', or None if translation fails
        """
        try:
            # Build translation prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(player_action, gm_response, turn_number)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call LLM
            response = await self.llm.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.3,  # Low temperature for consistent translation
                max_tokens=800    # Compressed output
            )
            
            if not response:
                logger.error("Translator: empty response from LLM")
                return None
            
            # Extract content from response structure
            try:
                content = response["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Translator: failed to extract content from response: {e}")
                logger.debug(f"Full response: {response}")
                return None
            
            if not content or content == "...":
                logger.error("Translator: empty or placeholder content from LLM")
                return None
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            if not content:
                logger.error("Translator: content empty after cleanup")
                return None
            
            # DON'T parse JSON - just return raw text!
            # LLM agents understand JSON-like structure even with syntax errors
            # This is for token efficiency, not for machine parsing
            
            # Extract cost info from API response
            cost = 0.0
            if "usage" in response:
                cost = response["usage"].get("cost", 0.0)
            
            # Log agent call for debugging
            log_agent_call(
                agent_name="translator",
                context=messages,
                response=content,  # Raw text, not parsed
                turn_number=turn_number
            )
            
            logger.info(
                f"Translated turn {turn_number}: "
                f"{len(player_action)} + {len(gm_response)} RU chars -> "
                f"{len(content)} EN chars (compression: {100 - int(len(content) * 100 / (len(player_action) + len(gm_response)))}%)"
            )
            
            # Return raw text with cost metadata
            return {
                "content": content,
                "cost": cost
            }
        except Exception as e:
            logger.error(f"Translator: error translating turn: {e}")
            return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for translator."""
        return """You are a game turn translator and structurizer. Your task:

1. Translate from Russian to English
2. Structure content in JSON-like format
3. Preserve all plot-important details, emotions, relationships, descriptions
4. Remove only RHETORICAL repetition (not content!)

## Important principles:

**PRESERVE (keep in English translation):**
- Character emotions, reactions, feelings
- NPC personality traits and mannerisms  
- Physical descriptions (appearance, clothing, etc.)
- Atmosphere and mood (if plot-relevant)
- Relationships between characters
- All plot details and consequences
- Dialog content and tone

**REDUCE (25-35% compression):**
- Repetitive phrasing ("again and again")
- Over-elaborate metaphors (keep essence, simplify wording)
- Excessive synonyms for same action
- Redundant narrative connectors

**Example transformation:**
❌ Bad (too aggressive): "Kира: silver hair, slim figure"
✅ Good (preserves details): "Kира: long silver curls flowing in moonlight, slender well-proportioned figure"

❌ Bad (loses emotion): "Two shots fired at agents"
✅ Good (preserves scene): "BAM-BAM! Two shotgun blasts tear through silence at point-blank range. First Weyland agent takes full load to chest - magical shield can't even form, body slams into wall leaving bloody trail. Second shot shatters another mage's knee - he falls screaming, clutching shattered bone."

Output JSON structure:
{
  "turn": <number>,
  "player_action": "Brief player action (1-2 sentences)",
  "gm_narrative": "Main GM response preserving ALL important details, emotions, descriptions. Can be 300-500 words if scene is rich. Don't cut plot content!",
  "dialogue": {
    "NPC_Name": "their words and tone"
  },
  "descriptions": {
    "NPCs": {"Name": "appearance, personality traits"},
    "locations": {"Place": "atmosphere, details"}
  },
  "key_events": ["event1", "event2"],
  "npcs_involved": ["Name1", "Name2"],
  "locations": ["Location1"],
  "items": ["Item1"],
  "changes": {
    "hp": <delta or null>,
    "mana": <delta or null>,
    "gold": <delta or null>,
    "xp": {"spades": <delta>, ...} or null
  }
}

Rules:
- Keep all Russian names (NPCs, locations, items) in Russian - use Cyrillic!
- Translate descriptions and narrative to English
- 25-35% compression through removing redundancy, NOT cutting content
- Preserve plot, emotions, relationships, descriptions
- If GM text is rich and detailed - keep it detailed in translation!
- Don't create structured fields if info not present (no hallucinations)
"""
    
    def _build_user_prompt(
        self,
        player_action: str,
        gm_response: str,
        turn_number: int
    ) -> str:
        """Build user prompt with turn data."""
        return f"""Turn #{turn_number}

Player action (RU):
{player_action}

GM response (RU):
{gm_response}

Translate and compress to English JSON:"""

