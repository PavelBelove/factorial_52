"""
Summarizer Agent - condenses conversation history.
Works in two modes: append and full rewrite.
"""
import logging
from typing import List, Dict, Any, Optional

from core.llm.openrouter_client import OpenRouterClient
from core.config import settings
from core.utils import get_prompt, PROMPT_SUMMARIZER_APPEND, PROMPT_SUMMARIZER_REWRITE

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    Summarizer Agent - condenses conversation history.
    
    Two modes:
    1. Append mode: Summary < threshold → append new turns to existing summary
    2. Rewrite mode: Summary >= threshold → rewrite entire summary, "drying" older events
    
    Responsibilities:
    - Condense history while preserving key events
    - Maintain quant name markers (=QuantName=)
    - Keep narrative coherence
    
    Does NOT:
    - Interpret or judge events
    - Create new quants
    - Affect dialogue style
    """
    
    def __init__(self, llm_client: OpenRouterClient, model: Optional[str] = None):
        """Initialize Summarizer agent."""
        self.llm = llm_client
        self.model = model  # Can override default model
    
    async def summarize(
        self,
        existing_summary: str,
        turns_to_summarize: List[Dict[str, str]],
        mode: str = "append"
    ) -> str:
        """
        Create or update summary.
        
        Args:
            existing_summary: Current summary text
            turns_to_summarize: Turns to process
            mode: "append" or "rewrite"
        
        Returns:
            New or updated summary text
        """
        if not turns_to_summarize:
            return existing_summary
        
        if mode == "append":
            return await self._append_mode(existing_summary, turns_to_summarize)
        elif mode == "rewrite":
            return await self._rewrite_mode(existing_summary, turns_to_summarize)
        else:
            logger.error(f"Unknown summarizer mode: {mode}")
            return existing_summary
    
    async def _append_mode(
        self,
        existing_summary: str,
        new_turns: List[Dict[str, str]]
    ) -> str:
        """
        Append mode: add summary of new turns to existing summary.
        Used when total summary length < threshold.
        """
        # Build context
        context = self._build_append_context(existing_summary, new_turns)
        
        # System prompt
        system_prompt = self._get_append_system_prompt()
        
        try:
            # Call LLM with max_tokens
            from core.config import settings
            new_summary_part = await self.llm.simple_completion(
                prompt=context,
                system_prompt=system_prompt,
                model=self.model,
                temperature=0.5,
                max_tokens=settings.summarizer_max_tokens
            )
            
            # Append to existing summary
            if existing_summary:
                return f"{existing_summary}\n\n{new_summary_part}"
            else:
                return new_summary_part
        
        except Exception as e:
            logger.error(f"Error in Summarizer (append mode): {e}")
            return existing_summary
    
    async def _rewrite_mode(
        self,
        existing_summary: str,
        all_turns: List[Dict[str, str]]
    ) -> str:
        """
        Rewrite mode: condense entire history.
        Used when summary exceeds threshold - "dries" older events.
        """
        # Build context
        context = self._build_rewrite_context(existing_summary, all_turns)
        
        # System prompt
        system_prompt = self._get_rewrite_system_prompt()
        
        try:
            # Call LLM
            new_summary = await self.llm.simple_completion(
                prompt=context,
                system_prompt=system_prompt,
                model=self.model,
                temperature=0.5,
                max_tokens=4000  # Limit summary length
            )
            
            return new_summary
        
        except Exception as e:
            logger.error(f"Error in Summarizer (rewrite mode): {e}")
            return existing_summary
    
    def _build_append_context(
        self,
        existing_summary: str,
        new_turns: List[Dict[str, str]]
    ) -> str:
        """Build context for append mode."""
        context_parts = []
        
        # Show last part of existing summary for context
        if existing_summary:
            # Get last 500 chars of summary
            summary_tail = existing_summary[-500:] if len(existing_summary) > 500 else existing_summary
            context_parts.append(f"# Предыдущее резюме (конец)\n\n...{summary_tail}")
        
        # New turns
        turns_text = []
        for turn in new_turns:
            turns_text.append(f"Игрок: {turn['user_message']}")
            turns_text.append(f"ГМ: {turn['agent_reply']}")
        
        context_parts.append(f"# Новые ходы для суммаризации\n\n" + "\n\n".join(turns_text))
        
        return "\n\n".join(context_parts)
    
    def _build_rewrite_context(
        self,
        existing_summary: str,
        all_turns: List[Dict[str, str]]
    ) -> str:
        """Build context for rewrite mode."""
        context_parts = []
        
        # Existing summary
        if existing_summary:
            context_parts.append(f"# Текущее резюме (слишком длинное)\n\n{existing_summary}")
        
        # Recent turns (for freshness)
        if all_turns:
            turns_text = []
            for turn in all_turns[-10:]:  # Last 10 turns
                turns_text.append(f"Игрок: {turn['user_message']}")
                turns_text.append(f"ГМ: {turn['agent_reply']}")
            
            context_parts.append(f"# Последние ходы\n\n" + "\n\n".join(turns_text))
        
        return "\n\n".join(context_parts)
    
    def _get_append_system_prompt(self) -> str:
        """System prompt for append mode - loaded from file."""
        return get_prompt(PROMPT_SUMMARIZER_APPEND)
    
    def _get_rewrite_system_prompt(self) -> str:
        """System prompt for rewrite mode - loaded from file."""
        return get_prompt(PROMPT_SUMMARIZER_REWRITE)
    
    def should_use_rewrite_mode(self, summary_text: str) -> bool:
        """Check if summary exceeds threshold and needs full rewrite."""
        return len(summary_text) >= settings.summary_append_threshold

