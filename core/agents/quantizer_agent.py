"""
Quantizer Agent - manages memory updates.
Creates, updates, and maintains quants based on dialogue history.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.models import Quant
from core.utils.agent_logger import log_agent_call

logger = logging.getLogger(__name__)


class QuantizerAgent:
    """
    Quantizer Agent - background memory maintenance.
    
    Responsibilities:
    - Create new quants
    - Update existing quants
    - Fix contradictions
    - Manage semantic links
    
    Does NOT:
    - Participate in dialogue
    - Influence narrative style
    - Choose which quants are active
    """
    
    def __init__(self, llm_client: OpenRouterClient, memory_manager, model: Optional[str] = None):
        """Initialize Quantizer agent."""
        self.llm = llm_client
        self.memory_manager = memory_manager
        self.model = model  # Can override default model
    
    async def process_memory_updates(
        self,
        session_id: int,
        summary_text: str,
        recent_turns: List[Dict[str, str]],
        active_quants: List[Quant],
        current_turn: int
    ) -> Dict[str, Any]:
        """
        Analyze recent dialogue and generate memory update commands.
        
        Args:
            summary_text: Current session summary
            recent_turns: Recent conversation turns
            active_quants: Currently active quants
            current_turn: Current turn number
        
        Returns:
            Dict with commands in format:
            {
                "create_EntityName": {full quant data},
                "append_EntityName_body_notes": "new note",
                "replace_EntityName_links_OtherEntity": "new relation",
                "delete_OldEntity": null
            }
        """
        # Build context for quantizer
        context = self._build_quantizer_context(
            session_id,
            summary_text,
            recent_turns,
            active_quants,
            current_turn
        )
        
        # System prompt for quantizer
        system_prompt = self._get_quantizer_system_prompt()
        
        try:
            # Call LLM with max_tokens
            from core.config import settings
            response = await self.llm.json_completion(
                prompt=context,
                system_prompt=system_prompt,
                model=self.model,
                temperature=0.5,  # Lower temperature for more consistent structure
                max_tokens=settings.quantizer_max_tokens
            )
            
            # Validate commands
            result = self._validate_commands(response)
            
            # Log agent call for debugging
            log_agent_call(
                agent_name="quantizer",
                context=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                response=result
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error in Quantizer agent: {e}")
            return {}
    
    def _build_quantizer_context(
        self,
        session_id: int,
        summary_text: str,
        recent_turns: List[Dict[str, str]],
        active_quants: List[Quant],
        current_turn: int
    ) -> str:
        """Build context for quantizer."""
        context_parts = []
        
        # Summary
        if summary_text:
            context_parts.append(f"# История сессии (краткая)\n\n{summary_text[:1000]}...")
        
        # Active quants
        if active_quants:
            quants_json = []
            for q in active_quants:
                quants_json.append({
                    "id": q.id,
                    "type": q.type.value,
                    "body": q.body,
                    "links": q.links,
                    "updated_at": q.updated_at
                })
            
            context_parts.append(
                f"# Активные кванты\n\n```json\n{json.dumps(quants_json, ensure_ascii=False, indent=2)}\n```"
            )
        
        # Synopsis of recent quants (quick navigation)
        synopsis_list = self.memory_manager.get_recent_quants_synopsis(
            session_id,
            current_turn
        )
        if synopsis_list:
            context_parts.append(f"# Доступные кванты (последние обновления)\n\n{synopsis_list}")
        
        # Recent turns
        turns_text = []
        for turn in recent_turns[-5:]:  # Last 5 turns
            turns_text.append(f"Игрок: {turn['user_message']}")
            turns_text.append(f"ГМ: {turn['agent_reply']}")
        
        if turns_text:
            context_parts.append(f"# Последние ходы\n\n" + "\n\n".join(turns_text))
        
        context_parts.append(f"\n# Текущий ход: {current_turn}")
        
        return "\n\n".join(context_parts)
    
    def _get_quantizer_system_prompt(self) -> str:
        """System prompt for Quantizer - loads from file."""
        try:
            from core.utils import get_prompt, PROMPT_QUANTIZER
            return get_prompt(PROMPT_QUANTIZER)
        except Exception as e:
            logger.error(f"Failed to load Quantizer prompt from file: {e}")
            # Fallback (should never happen)
            return """# Role: Memory Quantizer
You manage long-term memory. Create and update quants (atomic memory units) for NPCs, locations, items, events.
Write all content in ENGLISH, keep quant names/IDs in RUSSIAN."""
    
    def _validate_commands(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command structure."""
        if not isinstance(response, dict):
            logger.warning("Quantizer response is not a dict")
            return {}
        
        # Filter out invalid commands
        valid_commands = {}
        
        for key, value in response.items():
            # Check command format
            parts = key.split("_", 1)
            if len(parts) < 2:
                logger.warning(f"Invalid command format: {key}")
                continue
            
            action = parts[0].lower()
            
            if action not in ["create", "append", "replace", "delete"]:
                logger.warning(f"Unknown action: {action}")
                continue
            
            valid_commands[key] = value
        
        return valid_commands

