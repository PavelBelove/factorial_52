"""
Context Manager - assembles optimal context for each turn.
Combines system prompt, summary, raw turns, and activated quants.
"""
import logging
from typing import List, Dict, Any, Optional

from core.database.db_manager import DatabaseManager
from core.models import Quant
from core.config import settings
from core.utils import get_prompt, PROMPT_GM

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context assembly for agent turns.
    
    Responsibilities:
    - Build system prompts (modular, configurable)
    - Combine summary + raw turns + quants
    - Control context length
    - Format context for LLM
    """
    
    def __init__(self, db_manager: DatabaseManager, memory_manager=None):
        """Initialize context manager."""
        self.db = db_manager
        self.memory_manager = memory_manager
    
    def build_context(
        self,
        session_id: int,
        current_turn: int,
        active_quants: List[Quant],
        system_prompt_parts: Optional[Dict[str, str]] = None,
        module_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Build complete context for agent turn.
        
        Args:
            session_id: Session ID
            current_turn: Current turn number
            active_quants: Activated quants for this turn
            system_prompt_parts: Modular system prompt components
            module_data: Optional data from modules (game rules, emotions, etc.)
        
        Returns:
            List of messages for LLM
        """
        messages = []
        
        # 1. System prompt
        system_prompt = self._build_system_prompt(system_prompt_parts, module_data)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 2. Summary (if exists)
        summary_text = self._get_summary(session_id)
        if summary_text:
            messages.append({
                "role": "system",
                "content": f"# История сессии\n\n{summary_text}"
            })
        
        # 3. Active quants
        if active_quants:
            quants_text = self._format_quants(active_quants)
            messages.append({
                "role": "system",
                "content": f"# Активная память (кванты)\n\n{quants_text}"
            })
        
        # 3.5. Synopsis of recent quants (quick navigation)
        if self.memory_manager:
            synopsis_list = self.memory_manager.get_recent_quants_synopsis(
                session_id, 
                current_turn
            )
            if synopsis_list:
                messages.append({
                    "role": "system",
                    "content": f"# Доступные кванты (последние обновления)\n\n{synopsis_list}"
                })
        
        # 4. Recent raw turns
        turns = self._get_recent_turns(session_id, current_turn)
        for turn in turns:
            messages.append({
                "role": "user",
                "content": turn["user_message"]
            })
            messages.append({
                "role": "assistant",
                "content": turn["agent_reply"]
            })
        
        return messages
    
    def _build_system_prompt(
        self,
        parts: Optional[Dict[str, str]],
        module_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build modular system prompt.
        
        Parts can include:
        - base: Core agent role
        - setting: World/game setting
        - rules: Game rules or interaction guidelines
        - restrictions: Content restrictions (18+, etc.)
        - format: Response format instructions
        """
        if not parts:
            parts = {}
        
        # Default base prompt
        base = parts.get("base", self._default_base_prompt())
        
        prompt_sections = [base]
        
        # Add other sections
        for key in ["setting", "rules", "restrictions", "format"]:
            if key in parts:
                prompt_sections.append(parts[key])
        
        # Add module data if provided
        if module_data:
            for module_name, data in module_data.items():
                prompt_sections.append(f"# {module_name}\n{data}")
        
        return "\n\n".join(prompt_sections)
    
    def _default_base_prompt(self) -> str:
        """Default base system prompt for GM - loaded from file."""
        try:
            return get_prompt(PROMPT_GM)
        except FileNotFoundError:
            logger.warning("GM prompt file not found, using fallback")
            # Fallback prompt
            return """# Роль: Гейм-мастер

Ты - гейм-мастер текстовой RPG.

Ответ в формате JSON:
{"reply": "текст", "quants": ["квант1", "квант2"]}
"""
    
    def _get_summary(self, session_id: int) -> str:
        """Get combined summary text."""
        summaries = self.db.get_all_summaries(session_id)
        
        if not summaries:
            return ""
        
        # Combine all summaries
        summary_parts = [s.summary_text for s in summaries]
        return "\n\n---\n\n".join(summary_parts)
    
    def _format_quants(self, quants: List[Quant]) -> str:
        """Format quants for context."""
        if not quants:
            return ""
        
        formatted = []
        for quant in quants:
            quant_str = f"## {settings.quant_marker}{quant.id}{settings.quant_marker}\n"
            quant_str += f"**Тип:** {quant.type.value}\n\n"
            
            # Body
            if quant.body:
                quant_str += "**Содержание:**\n"
                for key, value in quant.body.items():
                    quant_str += f"- {key}: {value}\n"
                quant_str += "\n"
            
            # Links
            if quant.links:
                quant_str += "**Связи:**\n"
                for link_id, relation in quant.links.items():
                    quant_str += f"- {settings.quant_marker}{link_id}{settings.quant_marker}: {relation}\n"
            
            formatted.append(quant_str)
        
        return "\n".join(formatted)
    
    def _get_recent_turns(
        self,
        session_id: int,
        current_turn: int
    ) -> List[Dict[str, str]]:
        """
        Get recent raw turns.
        Returns RAW_TURNS_MIN to RAW_TURNS_MAX most recent turns.
        """
        # Get recent turns (up to max)
        turns = self.db.get_recent_turns(
            session_id,
            limit=20  # Fetch more than max to account for background processing latency
        )
        
        # Reverse to chronological order
        turns.reverse()
        
        # Convert to dict format
        return [
            {
                "user_message": turn.user_message,
                "agent_reply": turn.agent_reply
            }
            for turn in turns
        ]
    
    def should_trigger_summarization(self, session_id: int) -> bool:
        """Check if summarization should be triggered."""
        # Count raw turns
        recent_turns = self.db.get_recent_turns(
            session_id,
            limit=settings.raw_turns_max + 1
        )
        
        return len(recent_turns) > settings.raw_turns_max
    
    def get_turns_for_summarization(
        self,
        session_id: int
    ) -> tuple[List[Any], int]:
        """
        Get turns that need to be summarized.
        Returns: (turns_to_summarize, new_turns_start)
        """
        recent_turns = self.db.get_recent_turns(
            session_id,
            limit=20  # Fetch more to ensure we don't skip turns if backlog grows
        )
        
        # Get turns beyond the minimum window
        turns_to_summarize = recent_turns[settings.raw_turns_min:]
        
        if not turns_to_summarize:
            return [], 0
        
        # New raw window starts at the minimum
        new_turns_start = recent_turns[settings.raw_turns_min - 1].turn_number if len(recent_turns) >= settings.raw_turns_min else 0
        
        return turns_to_summarize, new_turns_start

