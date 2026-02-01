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
        module_data: Optional[Dict[str, Any]] = None,
        world_id: Optional[str] = None,
        user_settings: Optional[Dict[str, str]] = None,
        world_created: bool = True
    ) -> List[Dict[str, str]]:
        """
        Build complete context for agent turn.

        Args:
            session_id: Session ID
            current_turn: Current turn number
            active_quants: Activated quants for this turn
            system_prompt_parts: Modular system prompt components
            module_data: Optional data from modules (game rules, emotions, etc.)
            world_id: Optional world ID for world-specific prompts
            user_settings: User preferences (language, content_filter, difficulty)
            world_created: Flag for sandbox mode (use creator prompt if False)

        Returns:
            List of messages for LLM
        """
        messages = []

        # 1. System prompt
        system_prompt = self._build_system_prompt(system_prompt_parts, module_data, world_id, user_settings, world_created)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 2. Summary (if exists)
        summary_text = self._get_summary(session_id)
        if summary_text:
            logger.info(f"📜 Summary in context ({len(summary_text)} chars): {summary_text[:100]}...")
            messages.append({
                "role": "system",
                "content": f"# Session History\n\n{summary_text}"
            })
        
        # 3. Active quants
        if active_quants:
            quant_ids = [q.id for q in active_quants]
            logger.info(f"📚 Active quants in context ({len(quant_ids)}): {quant_ids}")
            quants_text = self._format_quants(active_quants)
            messages.append({
                "role": "system",
                "content": f"# Active Memory (Quants)\n\n{quants_text}"
            })
        
        # 3.5. Synopsis of recent quants (quick navigation)
        if self.memory_manager:
            synopsis_list = self.memory_manager.get_recent_quants_synopsis(
                session_id, 
                current_turn
            )
            if synopsis_list:
                # Count quants in synopsis
                import re
                quant_names = re.findall(r'- (\w+):', synopsis_list)
                logger.info(f"📋 Synopsis quants in context ({len(quant_names)}): {quant_names[:10]}...")
                messages.append({
                    "role": "system",
                    "content": f"# Available Quants (recent updates)\n\n{synopsis_list}"
            })
        
        # 4. Recent raw turns
        turns = self._get_recent_turns(session_id, current_turn)
        if turns:
            logger.info(f"💬 Raw turns in context: {len(turns)} turns")
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
        module_data: Optional[Dict[str, Any]],
        world_id: Optional[str] = None,
        user_settings: Optional[Dict[str, str]] = None,
        world_created: bool = True
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

        # Default base prompt (with user settings for language and content filter)
        base = parts.get("base", self._default_base_prompt(world_id, user_settings, world_created))
        
        prompt_sections = [base]
        
        # Add other sections
        for key in ["setting", "rules", "restrictions", "format"]:
            if key in parts:
                prompt_sections.append(parts[key])
        
        # Add module data if provided
        if module_data:
            # Handle game mechanics specially
            if "character_creation" in module_data:
                mechanics_section = self._format_character_creation(module_data["character_creation"])
                prompt_sections.append(mechanics_section)
                logger.info("Added character creation section to prompt")
            elif "character" in module_data:
                mechanics_section = self._format_mechanics(module_data)
                prompt_sections.append(mechanics_section)
                logger.info("Added game mechanics section to prompt")
        
        return "\n\n".join(prompt_sections)
    
    def _default_base_prompt(
        self,
        world_id: Optional[str] = None,
        user_settings: Optional[Dict[str, str]] = None,
        world_created: bool = True
    ) -> str:
        """Load world-specific GM system prompt with dynamic settings."""
        # Extract settings
        language = user_settings.get("language", "ru") if user_settings else "ru"
        content_filter = user_settings.get("content_filter", "safe") if user_settings else "safe"
        genre_prism = user_settings.get("genre_prism", "balanced") if user_settings else "balanced"

        # ALWAYS use world-specific prompt
        if not world_id:
            logger.error("No world_id provided for GM prompt!")
            raise ValueError("world_id is required for GM prompt")
        
        from core.config import world_manager
        world_prompt = world_manager.get_gm_system_prompt(
            world_id,
            language=language,
            content_filter=content_filter,
            genre_prism=genre_prism,
            world_created=world_created
        )
        
        if not world_prompt:
            logger.error(f"Failed to load GM prompt for world {world_id}")
            raise FileNotFoundError(f"GM prompt not found for world {world_id}")
        
        prompt_type = "CREATOR" if not world_created else "NARRATIVE"
        logger.info(f"Loaded {prompt_type} GM prompt for {world_id} (lang={language}, filter={content_filter}, prism={genre_prism})")
        return world_prompt
    
    def _get_summary(self, session_id: int) -> str:
        """
        Get summary text.
        
        Since summarizer in append mode returns full cumulative summary,
        we only need the LATEST summary (which already contains all history).
        """
        latest_summary = self.db.get_latest_summary(session_id)
        
        if not latest_summary:
            return ""
        
        return latest_summary.summary_text
    
    def _format_quants(self, quants: List[Quant]) -> str:
        """Format quants for context."""
        if not quants:
            return ""
        
        formatted = []
        for quant in quants:
            quant_str = f"## {settings.quant_marker}{quant.id}{settings.quant_marker}\n"
            quant_str += f"**Type:** {quant.type.value}\n\n"
            
            # Body
            if quant.body:
                quant_str += "**Content:**\n"
                for key, value in quant.body.items():
                    quant_str += f"- {key}: {value}\n"
                quant_str += "\n"
            
            # Links
            if quant.links:
                quant_str += "**Links:**\n"
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
        Get recent turns (prefer translated text when available).
        Returns RAW_TURNS_MIN to RAW_TURNS_MAX most recent turns.
        """
        # Get recent turns (up to max)
        turns = self.db.get_recent_turns(
            session_id,
            limit=20  # Fetch more than max to account for background processing latency
        )
        
        # Reverse to chronological order
        turns.reverse()
        
        # Convert to dict format, using translated text when available
        result = []
        for turn in turns:
            if turn.translated_json:
                # Use RAW translated text (JSON-like structure, no parsing!)
                # LLM understands it even with syntax errors - this is for token efficiency
                    result.append({
                    "user_message": f"Turn {turn.turn_number}:",
                    "agent_reply": turn.translated_json  # RAW text, no JSON parsing
                    })
            else:
                # No translation yet - use raw (Russian)
                result.append({
                    "user_message": turn.user_message,
                    "agent_reply": turn.agent_reply
                })
        
        return result
    
    def should_trigger_summarization(self, session_id: int) -> bool:
        """Check if summarization should be triggered."""
        # Count raw turns
        recent_turns = self.db.get_recent_turns(
            session_id,
            limit=settings.raw_turns_max + 1
        )
        
        should_trigger = len(recent_turns) >= settings.raw_turns_max
        logger.debug(
            f"Summarizer check: {len(recent_turns)} raw turns, "
            f"threshold {settings.raw_turns_max}, trigger={should_trigger}"
        )
        
        return should_trigger
    
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
        turns_to_summarize = recent_turns[settings.raw_turns_keep:]
        
        if not turns_to_summarize:
            return [], 0
        
        # New raw window starts at the minimum
        new_turns_start = recent_turns[settings.raw_turns_keep - 1].turn_number if len(recent_turns) >= settings.raw_turns_keep else 0
        
        return turns_to_summarize, new_turns_start
    
    # =========================================================================
    # GAME MECHANICS FORMATTING
    # =========================================================================
    
    def _format_character_creation(self, creation_data: Dict[str, Any]) -> str:
        """Format character creation data for GM context"""
        instructions = creation_data["instructions"]
        
        return f"""# 🎲 Character Creation (Factorial 52! system)

{instructions}

---

**GM Instructions:**
1. Show player the cards and explain rules (text above - in player's language)
2. Wait for player's choice:
   - If wants to assign manually - let them say which card to which stat
   - If asks "optimal" - assign by suit matches
3. After assignment, return in `response_data`:

```json
{{
  "character_created": true,
  "create_character": {{
    "spades": 45,
    "hearts": 70,
    "diamonds": 35,
    "clubs": 75
  }}
}}
```

**Stat calculation:**
- Value = card rank × 5
- If card suit = stat suit, add +10

**Example:**
Card 7♠ to Strength (♠): 7×5 + 10 = 45
Card 7♠ to Magic (♥): 7×5 + 0 = 35

**DO NOT request "Character" or "Inventory" quants** - they are in game mechanics now!
"""
    
    def _format_mechanics(self, module_data: Dict[str, Any]) -> str:
        """Format full game mechanics data for GM context (compact ~300 tokens)"""
        logger.debug(f"Formatting mechanics. Module data keys: {module_data.keys()}")
        char = module_data["character"]
        cards = module_data["cards"]
        thresholds = module_data["thresholds"]
        checks = module_data["checks"]
        combat = module_data["combat"]
        logger.debug(f"Character stats: spades={char['spades']}, hearts={char['hearts']}, diamonds={char['diamonds']}, clubs={char['clubs']}")
        
        # Format cards
        pairs_str = []
        for pair in cards["pairs"]:
            cards_str = " + ".join(pair["cards"])
            pairs_str.append(f"Pair {pair['pair']}: {cards_str}")
        
        # Format special events
        special_events_str = ""
        if cards["special_events"]:
            special_events_str = "\n🎴 **Special events (peaceful time only):**\n" + "\n".join([f"- {event}" for event in cards["special_events"]])
        
        # Format inventory (compact)
        inventory_str = ""
        if char["inventory"]:
            equipped = [item["id"] for item in char["inventory"] if item.get("equipped")]
            not_equipped = [item["id"] for item in char["inventory"] if not item.get("equipped")]
            inventory_lines = []
            if equipped:
                inventory_lines.append(f"Equipped: {', '.join(equipped)}")
            if not_equipped:
                inventory_lines.append(f"Bag: {', '.join(not_equipped)}")
            inventory_str = "\n".join(inventory_lines)
        else:
            inventory_str = "Empty"

        # Format thresholds ONCE (same for all suits - based on average stat)
        # Get thresholds from any suit (they're all the same)
        any_suit_thresholds = thresholds["spades"]
        thresholds_str = f"Easy {any_suit_thresholds['easy']} | Normal {any_suit_thresholds['normal']} | Hard {any_suit_thresholds['hard']} | Very Hard {any_suit_thresholds['very_hard']}"
        
        # Format checks with FULL BREAKDOWN from pair 1 (no thresholds per line)
        pair1_checks = checks["pair_1"]
        checks_str = []
        for suit in ["spades", "hearts", "diamonds", "clubs"]:
            check = pair1_checks[suit]
            total = check["total"]
            suit_icon = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}[suit]
            
            # Show breakdown: card1 + card2 + stat
            card1_base = check['card1']['base']
            card1_bonus = check['card1']['bonus']
            card2_base = check['card2']['base']
            card2_bonus = check['card2']['bonus']
            stat = check['stat_value']
            
            card1_str = f"{card1_base}+{card1_bonus}" if card1_bonus > 0 else str(card1_base)
            card2_str = f"{card2_base}+{card2_bonus}" if card2_bonus > 0 else str(card2_base)
            breakdown = f"({card1_str} + {card2_str} + {stat} stat)"
            
            checks_str.append(f"{suit_icon}: {total} {breakdown}")
        
        # Format combat (show only best options from pair 1)
        pair1_combat = combat["pair_1"]
        melee_total = pair1_combat["melee_attack"]["total"]
        ranged_total = pair1_combat["ranged_attack"]["total"]
        phys_def_total = pair1_combat["physical_defense"]["total"]
        magic_def_total = pair1_combat["magic_defense"]["total"]
        
        mechanics_text = f"""# 🎲 Game Mechanics

## Character
**HP**: {char['hp']}/{char['max_hp']} | **Mana**: {char['mana']}/{char['max_mana']} | **Gold**: {char['gold']}

**Stats** (avg: {char['average']}):
♠ STR: {char['spades']} | ♥ MAG: {char['hearts']} | ♦ STA: {char['diamonds']} | ♣ AGI: {char['clubs']}

## 🎴 Cards (hidden from player)
{chr(10).join(pairs_str)}{special_events_str}

## 🎯 Checks (pair 1)
**Thresholds:** {thresholds_str}
{chr(10).join(checks_str)}

## ⚔️ Combat (pair 1)
Attack: melee {melee_total} | ranged {ranged_total}
Defense: physical {phys_def_total} | magical {magic_def_total}

## 🎒 Inventory ({len(char['inventory'])}/20)
{inventory_str}

---
**Instructions:**
1. Calculations DONE - pick appropriate result
2. Describe action narratively using ready values
3. In `response_data` specify changes:
```json
{{
  "checks_used": [{{"suit": "spades", "success": true}}],
  "hp": -15, "mana": -10, "gold": 100,
  "inventory": {{"add": [...], "remove": ["id"]}}
}}
```
4. Special events ONLY in peaceful time, NOT in combat
"""
        
        # Log the formatted mechanics for debugging
        logger.info(f"Formatted mechanics block:\n{mechanics_text}")
        
        return mechanics_text

