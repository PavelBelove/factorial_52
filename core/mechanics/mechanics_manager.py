"""
Main mechanics manager for PlexMem RPG system.
Coordinates card deck, calculations, and character state.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

import logging
from core.database.db_manager import DatabaseManager
from .card_deck import CardDeck
from .models import Card, Character, Item, Suit, ItemType
from . import calculations

logger = logging.getLogger(__name__)


class MechanicsManager:
    """
    Main manager for game mechanics.
    
    Responsibilities:
    - Draw cards for each turn
    - Calculate all checks and combat options
    - Manage character state (HP, mana, stats, inventory)
    - Apply changes from GM responses
    - Auto-level characters (XP → stat increases)
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.deck = CardDeck()
    
    # =========================================================================
    # CHARACTER MANAGEMENT
    # =========================================================================
    
    def character_exists(self, session_id: int) -> bool:
        """Check if character exists for session"""
        char = self.db.get_character(session_id)
        return char is not None
    
    def get_character(self, session_id: int) -> Optional[Character]:
        """Get character for session"""
        char_db = self.db.get_character(session_id)
        if not char_db:
            return None
        
        # Convert DB model to Pydantic model
        return self._db_to_character(char_db)
    
    def create_character(
        self,
        session_id: int,
        stats: Dict[str, int]
    ) -> Character:
        """
        Create new character with given stats.
        
        Args:
            session_id: Session ID
            stats: Initial stats {"spades": 45, "hearts": 70, ...}
            
        Returns:
            Created character
        """
        # Calculate starting HP and mana
        hp, max_hp, mana, max_mana = calculations.calculate_starting_hp_mana(stats)
        
        # Create in DB
        char_db = self.db.create_character(
            session_id=session_id,
            spades=stats["spades"],
            hearts=stats["hearts"],
            diamonds=stats["diamonds"],
            clubs=stats["clubs"],
            hp=hp,
            max_hp=max_hp,
            mana=mana,
            max_mana=max_mana,
            gold=50  # Starting gold
        )
        
        logger.info(f"Created character for session {session_id}: {stats}")
        return self._db_to_character(char_db)
    
    def get_character_state(self, session_id: int) -> Dict[str, Any]:
        """
        Get full character state for context.
        
        Returns:
            Dict with all character data formatted for GM context
        """
        char = self.get_character(session_id)
        if not char:
            return {}
        
        return {
            "spades": char.spades,
            "hearts": char.hearts,
            "diamonds": char.diamonds,
            "clubs": char.clubs,
            "hp": char.hp,
            "max_hp": char.max_hp,
            "mana": char.mana,
            "max_mana": char.max_mana,
            "gold": char.gold,
            "inventory": [self._item_to_dict(item) for item in char.inventory],
            "equipped": char.equipped,
            "average": char.average_stat
        }
    
    # =========================================================================
    # CARD DRAWING
    # =========================================================================
    
    def draw_cards_for_turn(self) -> Dict[str, Any]:
        """
        Draw cards for a turn (always 2 pairs = 4 cards).
        
        Returns:
            Dict with cards and special events
        """
        pairs = self.deck.draw_pairs(num_pairs=2)
        
        # Flatten all cards for special event detection
        all_cards = []
        for pair in pairs:
            all_cards.extend(pair)
        
        # Detect special events (only for peaceful time, only for player)
        special_events = calculations.detect_special_events(all_cards)
        
        return {
            "pairs": [
                {"pair": 1, "cards": [str(card) for card in pairs[0]]},
                {"pair": 2, "cards": [str(card) for card in pairs[1]]}
            ],
            "special_events": special_events,
            "_card_objects": pairs  # Keep for calculations
        }
    
    def generate_character_cards(self) -> Dict[str, Any]:
        """
        Generate 5 cards for character creation.
        
        Returns:
            Dict with cards and detailed instructions
        """
        cards = self.deck.draw(5)
        cards_str = [str(card) for card in cards]
        
        # Calculate values for each card
        card_details = []
        for idx, card in enumerate(cards):
            base_value = card.rank * 5
            details = {
                "card": str(card),
                "base": base_value,
                "with_bonus": base_value + 10,
                "suit": card.suit.value,
                "index": idx
            }
            card_details.append(details)
        
        # Sort to find worst
        sorted_by_value = sorted(card_details, key=lambda x: x["base"])
        worst_card = sorted_by_value[0]
        
        # Build detailed instructions
        instructions = f"""🎲 **СОЗДАНИЕ ПЕРСОНАЖА** (система "Факториал 52!")

Вытянуто 5 карт. Нужно распределить 4 лучших по характеристикам (худшая не учитывается).

**Вытянутые карты:**
"""
        for detail in card_details:
            is_worst = (detail["index"] == worst_card["index"])
            worst_mark = " ❌ **ХУДШАЯ - не учитывается**" if is_worst else ""
            instructions += f"{detail['index'] + 1}. {detail['card']} → {detail['base']} очков (+10 если совпадёт масть = {detail['with_bonus']}){worst_mark}\n"
        
        instructions += f"""
**Правила распределения:**
- Каждую карту назначаешь на одну характеристику
- Значение = номинал × 5
- **БОНУС +10 если масть карты совпадает с характеристикой!**

**Характеристики (масти):**
♠ **Сила** (Пики): ближний бой, физическая сила, воля, запугивание
♥ **Магия** (Червы): магическая защита, колдовство, мудрость, общение
♦ **Стойкость** (Бубны): физическая защита, выносливость, харизма, торговля
♣ **Ловкость** (Трефы): дальний бой, акробатика, меткость, скрытность

**Что ты можешь сделать:**
1. Распределить карты самостоятельно (скажи как)
2. Попросить меня распределить оптимально (я выберу лучшие совпадения)

Напиши что выбираешь, и я зафиксирую характеристики!
"""
        
        return {
            "cards": cards_str,
            "instructions": instructions,
            "card_details": card_details,
            "_card_objects": cards  # Keep for stat calculation
        }
    
    # =========================================================================
    # CALCULATIONS
    # =========================================================================
    
    def calculate_thresholds(self, session_id: int) -> Dict[str, Any]:
        """Calculate difficulty thresholds for all suits"""
        char = self.get_character(session_id)
        if not char:
            return {}
        
        return calculations.calculate_thresholds(char)
    
    def calculate_all_checks(
        self,
        session_id: int,
        cards_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate all possible checks for all pairs and all suits"""
        char = self.get_character(session_id)
        if not char:
            return {}
        
        thresholds = self.calculate_thresholds(session_id)
        card_pairs = cards_data["_card_objects"]
        
        return calculations.calculate_all_checks(card_pairs, char, thresholds)
    
    def calculate_all_combat_options(
        self,
        session_id: int,
        cards_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate all possible combat actions for all pairs"""
        char = self.get_character(session_id)
        if not char:
            return {}
        
        card_pairs = cards_data["_card_objects"]
        
        return calculations.calculate_all_combat_options(card_pairs, char)
    
    # =========================================================================
    # APPLYING GM CHANGES
    # =========================================================================
    
    def apply_gm_changes(
        self,
        session_id: int,
        response_data: Dict[str, Any]
    ):
        """
        Apply changes from GM response.
        
        GM can return:
        {
            "hp": -15,  # Change HP
            "mana": -10,  # Change mana
            "gold": 100,  # Change gold
            "checks_used": [  # Checks that were used (for XP)
                {"suit": "spades", "success": true},
                {"suit": "hearts", "success": false}
            ],
            "inventory": {
                "add": [{"id": "Меч", "type": "weapon", "suit": "♠", "bonus": 25, ...}],
                "remove": ["Старый_меч"]
            },
            "equip": ["Меч"],
            "unequip": ["Щит"],
            "stats": {"spades": 10}  # Direct stat increase (e.g., from training)
        }
        
        Args:
            session_id: Session ID
            response_data: Data from GM response
        """
        char = self.get_character(session_id)
        if not char:
            logger.warning(f"No character for session {session_id}, cannot apply changes")
            return
        
        changes_applied = []
        
        # HP changes
        if "hp" in response_data:
            char.hp = max(0, min(char.max_hp, char.hp + response_data["hp"]))
            changes_applied.append(f"HP: {response_data['hp']:+d}")
        
        # Mana changes
        if "mana" in response_data:
            char.mana = max(0, min(char.max_mana, char.mana + response_data["mana"]))
            changes_applied.append(f"Mana: {response_data['mana']:+d}")
        
        # Gold changes
        if "gold" in response_data:
            char.gold = max(0, char.gold + response_data["gold"])
            changes_applied.append(f"Gold: {response_data['gold']:+d}")
        
        # Process successful checks (add XP)
        if "checks_used" in response_data:
            for check in response_data["checks_used"]:
                if check.get("success"):
                    suit_name = check["suit"]
                    self._add_xp(char, suit_name)
                    changes_applied.append(f"XP +1 для {suit_name}")
        
        # Direct stat increases (from training, etc.)
        if "stats" in response_data:
            for suit_name, increase in response_data["stats"].items():
                current = getattr(char, suit_name)
                setattr(char, suit_name, current + increase)
                changes_applied.append(f"{suit_name}: +{increase}")
                
                # Also increase HP/mana for each stat increase
                char.max_hp += increase
                char.max_mana += increase
        
        # Inventory changes
        if "inventory" in response_data:
            inv_data = response_data["inventory"]
            
            # Remove items
            if "remove" in inv_data:
                for item_id in inv_data["remove"]:
                    char.inventory = [item for item in char.inventory if item.id != item_id]
                    changes_applied.append(f"Удалён: {item_id}")
            
            # Add items
            if "add" in inv_data:
                for item_data in inv_data["add"]:
                    item = Item(**item_data)
                    char.inventory.append(item)
                    changes_applied.append(f"Получен: {item.id}")
        
        # Equip/unequip items
        if "equip" in response_data:
            for item_id in response_data["equip"]:
                for item in char.inventory:
                    if item.id == item_id:
                        item.equipped = True
                        char.equipped[item_id] = True
                        changes_applied.append(f"Надето: {item_id}")
        
        if "unequip" in response_data:
            for item_id in response_data["unequip"]:
                for item in char.inventory:
                    if item.id == item_id:
                        item.equipped = False
                        char.equipped.pop(item_id, None)
                        changes_applied.append(f"Снято: {item_id}")
        
        # Save to DB
        self._character_to_db(session_id, char)
        
        if changes_applied:
            logger.info(f"Applied changes for session {session_id}: {', '.join(changes_applied)}")
    
    def _add_xp(self, char: Character, suit_name: str):
        """
        Add XP to character and auto-level if needed.
        
        At 10 XP:
        - +1 to stat
        - +1 to max_hp
        - +1 to max_mana
        - Reset XP to 0
        """
        xp_field = f"{suit_name}_xp"
        current_xp = getattr(char, xp_field)
        current_xp += 1
        
        if current_xp >= 10:
            # Level up!
            current_stat = getattr(char, suit_name)
            setattr(char, suit_name, current_stat + 1)
            setattr(char, xp_field, 0)
            
            # Also increase HP and mana
            char.max_hp += 1
            char.max_mana += 1
            
            logger.info(f"Character leveled up: {suit_name} {current_stat} → {current_stat + 1}")
        else:
            setattr(char, xp_field, current_xp)
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _db_to_character(self, char_db) -> Character:
        """Convert DB model to Pydantic Character"""
        # Parse inventory JSON
        inventory = []
        if char_db.inventory:
            for item_data in char_db.inventory:
                if isinstance(item_data, dict):
                    # Convert suit string back to Suit enum if present
                    if "suit" in item_data and item_data["suit"]:
                        item_data["suit"] = Suit(item_data["suit"])
                    inventory.append(Item(**item_data))
        
        return Character(
            session_id=char_db.session_id,
            spades=char_db.spades,
            hearts=char_db.hearts,
            diamonds=char_db.diamonds,
            clubs=char_db.clubs,
            spades_xp=char_db.spades_xp,
            hearts_xp=char_db.hearts_xp,
            diamonds_xp=char_db.diamonds_xp,
            clubs_xp=char_db.clubs_xp,
            hp=char_db.hp,
            max_hp=char_db.max_hp,
            mana=char_db.mana,
            max_mana=char_db.max_mana,
            gold=char_db.gold,
            inventory=inventory,
            equipped=char_db.equipped or {},
            created_at=int(char_db.created_at.timestamp()) if char_db.created_at else 0,
            updated_at=int(char_db.updated_at.timestamp()) if char_db.updated_at else 0
        )
    
    def _character_to_db(self, session_id: int, char: Character):
        """Save Character to database"""
        # Convert inventory to dict
        inventory_data = []
        for item in char.inventory:
            item_dict = item.dict()
            # Convert Suit enum to string for JSON storage
            if item_dict.get("suit"):
                item_dict["suit"] = item_dict["suit"].value
            inventory_data.append(item_dict)
        
        self.db.update_character(
            session_id=session_id,
            spades=char.spades,
            hearts=char.hearts,
            diamonds=char.diamonds,
            clubs=char.clubs,
            spades_xp=char.spades_xp,
            hearts_xp=char.hearts_xp,
            diamonds_xp=char.diamonds_xp,
            clubs_xp=char.clubs_xp,
            hp=char.hp,
            max_hp=char.max_hp,
            mana=char.mana,
            max_mana=char.max_mana,
            gold=char.gold,
            inventory=inventory_data,
            equipped=char.equipped
        )
    
    def _item_to_dict(self, item: Item) -> Dict[str, Any]:
        """Convert Item to dict for context"""
        item_dict = item.dict()
        if item_dict.get("suit"):
            item_dict["suit"] = item_dict["suit"].value
        return item_dict

