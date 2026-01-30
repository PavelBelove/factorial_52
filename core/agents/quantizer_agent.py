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
        synopsis_list: str,
        current_turn: int,
        world_id: Optional[str] = None,
        language: str = "Russian"
    ) -> Dict[str, Any]:
        """
        Analyze recent dialogue and generate memory update commands.

        Args:
            summary_text: Current session summary
            recent_turns: Recent conversation turns
            active_quants: Currently active quants
            synopsis_list: Synopsis of recent quants for navigation
            current_turn: Current turn number
            world_id: World ID for world-specific instructions (optional)
            language: User's language for quant names (default: Russian)

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
            synopsis_list,
            current_turn
        )

        # System prompt for quantizer (with world-specific instructions if available)
        system_prompt = self._get_quantizer_system_prompt(world_id, language=language)
        
        try:
            # Call LLM with max_tokens - get raw response first
            from core.config import settings

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ]

            raw_response = await self.llm.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.5,
                max_tokens=settings.quantizer_max_tokens,
                response_format={"type": "json_object"}
            )

            # Extract and log raw content BEFORE parsing
            raw_content = self.llm.extract_content(raw_response)
            logger.info(f"Quantizer raw response ({len(raw_content)} chars): {raw_content[:500]}...")

            # Parse JSON
            response = self.llm.extract_json(raw_response)

            # Check for empty response
            if not response:
                logger.warning(f"Quantizer: extract_json returned empty dict. Raw content was: {raw_content[:1000]}")

            # Validate commands
            result = self._validate_commands(response)

            # Log result
            if result:
                logger.info(f"Quantizer generated {len(result)} commands: {list(result.keys())}")
            else:
                logger.info("Quantizer: no memory updates needed (empty response)")

            # Log agent call for debugging - include raw content
            log_agent_call(
                agent_name="quantizer",
                context=messages,
                response={"raw_content": raw_content, "parsed": result}
            )

            return result

        except Exception as e:
            logger.error(f"Error in Quantizer agent: {e}", exc_info=True)
            return {}
    
    def _build_quantizer_context(
        self,
        session_id: int,
        summary_text: str,
        recent_turns: List[Dict[str, str]],
        active_quants: List[Quant],
        synopsis_list: str,
        current_turn: int
    ) -> str:
        """Build context for quantizer."""
        context_parts = []
        
        # Summary
        if summary_text:
            context_parts.append(f"# История сессии (краткая)\n\n{summary_text[:1000]}...")
        
        # Synopsis list (navigation)
        if synopsis_list:
            context_parts.append(f"# Доступные кванты (недавно обновленные)\n\n{synopsis_list}")
        
        # Active quants
        if active_quants:
            quants_json = []
            for q in active_quants:
                quant_data = {
                    "id": q.id,
                    "type": q.type.value,
                    "body": q.body,
                    "links": q.links,
                    "updated_at": q.updated_at
                }
                # Add warning flag if quant needs summarization
                if q.needs_summarization:
                    quant_data["⚠️ needs_summarization"] = True
                quants_json.append(quant_data)
            
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
    
    def _get_quantizer_system_prompt(self, world_id: Optional[str] = None, language: str = "Russian") -> str:
        """
        System prompt for Quantizer - combines base prompt with world-specific instructions.
        Base prompt contains command format and general rules.
        World-specific instructions add world-specific guidance.

        Args:
            world_id: World ID for world-specific instructions
            language: User's language for template rendering
        """
        template_vars = {"language": language}

        try:
            # Load and render base prompt (contains command format, general rules)
            from core.utils import render_prompt, render_world_prompt, PROMPT_QUANTIZER
            base_prompt = render_prompt(PROMPT_QUANTIZER, variables=template_vars)
            logger.info(f"Loaded base Quantizer prompt (language: {language})")

            # Try to load world-specific instructions
            if world_id:
                from core.config import world_manager
                world_instructions = world_manager.get_quantizer_instructions(world_id)

                if world_instructions:
                    # Render world prompt with same variables
                    rendered_world = render_world_prompt(world_instructions, variables=template_vars)
                    # COMBINE base + world-specific
                    combined = f"{base_prompt}\n\n---\n\n# World-Specific Instructions: {world_id}\n\n{rendered_world}"
                    logger.info(f"Combined base prompt with world-specific instructions for: {world_id}")
                    return combined

            return base_prompt

        except Exception as e:
            logger.error(f"Failed to load Quantizer prompt from file: {e}")
            # Fallback
            return f"""# Role: Memory Quantizer
You manage long-term memory. Create and update quants (atomic memory units) for NPCs, locations, items, events.
Write quant names/IDs in {language}. Write all content (synopsis, body, links) in English.

## Command Format
Return JSON with commands:
- "create_Name": {{type, synopsis, body, links}} - create new quant
- "append_Name_field": "value" - add to existing field
- "replace_Name_field": "value" - replace field value
- "delete_Name": null - delete quant"""
    
    def _validate_commands(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command structure."""
        if not isinstance(response, dict):
            logger.warning("Quantizer response is not a dict")
            return {}

        # Check if response is a raw quant structure instead of commands
        # LLM sometimes returns {"id": "...", "type": "...", "body": {...}}
        # instead of {"create_Name": {...}}
        if "id" in response and ("type" in response or "body" in response or "synopsis" in response):
            logger.info("Detected raw quant format, converting to create command")
            quant_id = response.pop("id")
            return {f"create_{quant_id}": response}

        # Check if response is a list of quants
        if isinstance(response, list):
            logger.info(f"Detected list of {len(response)} quants, converting to create commands")
            commands = {}
            for item in response:
                if isinstance(item, dict) and "id" in item:
                    quant_id = item.pop("id")
                    commands[f"create_{quant_id}"] = item
            return commands

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

