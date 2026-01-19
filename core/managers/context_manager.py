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
    
    # =========================================================================
    # GAME MECHANICS FORMATTING
    # =========================================================================
    
    def _format_character_creation(self, creation_data: Dict[str, Any]) -> str:
        """Format character creation data for GM context"""
        instructions = creation_data["instructions"]
        
        return f"""# 🎲 Создание персонажа (система "Факториал 52!")

{instructions}

---

**Инструкция для ГМ:**
1. Покажи игроку карты и объясни правила (текст выше)
2. Дождись его выбора:
   - Если хочет распределить сам - пусть скажет какую карту куда
   - Если просит "оптимально" - распредели по совпадениям мастей
3. После распределения верни в `response_data`:

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

**Расчет характеристик:**
- Значение = номинал карты × 5
- Если масть карты = масть характеристики, добавь +10

**Пример:**
Карта 7♠ на Силу (♠): 7×5 + 10 = 45
Карта 7♠ на Магию (♥): 7×5 + 0 = 35

**НЕ запрашивай кванты "Character" или "Inventory"** - это теперь отдельная система!
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
            pairs_str.append(f"Пара {pair['pair']}: {cards_str}")
        
        # Format special events
        special_events_str = ""
        if cards["special_events"]:
            special_events_str = "\n🎴 **Особые события (только вне боя):**\n" + "\n".join([f"- {event}" for event in cards["special_events"]])
        
        # Format inventory (compact)
        inventory_str = ""
        if char["inventory"]:
            equipped = [item["id"] for item in char["inventory"] if item.get("equipped")]
            not_equipped = [item["id"] for item in char["inventory"] if not item.get("equipped")]
            inventory_lines = []
            if equipped:
                inventory_lines.append(f"✅ Надето: {', '.join(equipped)}")
            if not_equipped:
                inventory_lines.append(f"📦 В сумке: {', '.join(not_equipped)}")
            inventory_str = "\n".join(inventory_lines)
        else:
            inventory_str = "Пусто"
        
        # Format checks with FULL BREAKDOWN from pair 1
        pair1_checks = checks["pair_1"]
        checks_str = []
        for suit in ["spades", "hearts", "diamonds", "clubs"]:
            check = pair1_checks[suit]
            total = check["total"]
            easy_thresh = thresholds[suit]["easy"]
            hard_thresh = thresholds[suit]["hard"]
            suit_icon = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}[suit]
            
            # Show breakdown: card1 + card2 + stat
            card1_base = check['card1']['base']
            card1_bonus = check['card1']['bonus']
            card2_base = check['card2']['base']
            card2_bonus = check['card2']['bonus']
            stat = check['stat_value']
            
            card1_str = f"{card1_base}+{card1_bonus}" if card1_bonus > 0 else str(card1_base)
            card2_str = f"{card2_base}+{card2_bonus}" if card2_bonus > 0 else str(card2_base)
            breakdown = f"({card1_str} + {card2_str} + {stat} стат)"
            
            checks_str.append(f"{suit_icon}: {total} {breakdown} → легко {easy_thresh}, сложно {hard_thresh}")
        
        # Format combat (show only best options from pair 1)
        pair1_combat = combat["pair_1"]
        melee_total = pair1_combat["melee_attack"]["total"]
        ranged_total = pair1_combat["ranged_attack"]["total"]
        phys_def_total = pair1_combat["physical_defense"]["total"]
        magic_def_total = pair1_combat["magic_defense"]["total"]
        
        mechanics_text = f"""# 🎲 Игровые механики

## Персонаж
**HP**: {char['hp']}/{char['max_hp']} | **Мана**: {char['mana']}/{char['max_mana']} | **Золото**: {char['gold']}

**Характеристики** (среднее: {char['average']}):
♠ Сила: {char['spades']} | ♥ Магия: {char['hearts']} | ♦ Стойкость: {char['diamonds']} | ♣ Ловкость: {char['clubs']}

## 🎴 Карты (игрок НЕ видит, вытянуты случайно)
{chr(10).join(pairs_str)}{special_events_str}

## 🎯 Готовые расчёты проверок (пара 1)
{chr(10).join(checks_str)}

## ⚔️ Готовые расчёты боя (пара 1)
Атака: ближняя {melee_total} | дальняя {ranged_total}
Защита: физ. {phys_def_total} | маг. {magic_def_total}
Комбо: доступно (используются те же карты)

## 🎒 Инвентарь ({len(char['inventory'])}/20)
{inventory_str}

---
**Инструкции:**
1. Все расчёты УЖЕ СДЕЛАНЫ - просто выбери подходящий результат
2. Опиши действие сюжетно, используя готовые значения
3. В `response_data` укажи изменения и какие проверки были использованы:
```json
{{
  "checks_used": [{{"suit": "spades", "success": true}}],
  "hp": -15,
  "mana": -10,
  "gold": 100,
  "inventory": {{
    "add": [{{"id": "Меч", "type": "weapon", "suit": "♠", "bonus": 25, "description": "..."}}],
    "remove": ["Старый_меч"]
  }},
  "equip": ["Меч"]
}}
```
4. Особые события (фигуры) используй ТОЛЬКО в мирное время
5. В бою фигуры НЕ учитываются
"""
        
        # Log the formatted mechanics for debugging
        logger.info(f"Formatted mechanics block:\n{mechanics_text}")
        
        return mechanics_text

