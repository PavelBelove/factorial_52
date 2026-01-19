"""
Game mechanics models for PlexMem RPG system.
Based on "Factorial 52!" tabletop RPG rules.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Suit(str, Enum):
    """Card suits mapping to character stats"""
    SPADES = "♠"    # Strength, melee combat
    HEARTS = "♥"    # Magic, magical defense
    DIAMONDS = "♦"  # Endurance, physical defense
    CLUBS = "♣"     # Agility, ranged combat


class Card:
    """
    A playing card. NOT stored in DB - generated each turn.
    
    Rank values:
    - 2-10: face value
    - Jack (J): 11
    - Queen (Q): 12
    - King (K): 13
    - Ace (A): 15
    """
    def __init__(self, rank: int, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.color = "red" if suit in [Suit.HEARTS, Suit.DIAMONDS] else "black"
        self.is_face = rank in [11, 12, 13]  # Jack, Queen, King
        
    def __str__(self) -> str:
        """Format as 'K♠', '8♥', etc."""
        rank_str = {11: 'J', 12: 'Q', 13: 'K', 15: 'A'}.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def face_meaning(self) -> Optional[str]:
        """Special meaning for face cards (only in peaceful time)"""
        if self.rank == 11:  # Jack
            return "Неожиданный поворот или появление NPC"
        elif self.rank == 12:  # Queen
            return "Влияние женского персонажа/энергии"
        elif self.rank == 13:  # King
            return "Влияние мужского персонажа/энергии"
        return None
    
    @property
    def value(self) -> int:
        """Base value for calculations (rank × 10)"""
        return self.rank * 10


class ItemType(str, Enum):
    """Types of items"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    RING = "ring"
    BRACELET = "bracelet"
    CLOAK = "cloak"
    AMULET = "amulet"
    BELT = "belt"
    BOOTS = "boots"
    GLOVES = "gloves"
    HELMET = "helmet"


class Item(BaseModel):
    """
    Item in character's inventory.
    """
    id: str = Field(..., description="Unique item ID (e.g. 'Меч_кладенец')")
    type: ItemType = Field(..., description="Item type")
    suit: Optional[Suit] = Field(None, description="Suit for bonus (None for consumables)")
    bonus: int = Field(0, description="Bonus to characteristic")
    description: str = Field("", description="Item description")
    equipped: bool = Field(False, description="Whether item is currently equipped")
    quantity: int = Field(1, description="Quantity (for stackable consumables)")


class Character(BaseModel):
    """
    Character data (stored in DB).
    
    Starting values:
    - mana = hearts × 3
    - max_hp = spades + diamonds + clubs
    - hp = max_hp
    - max_mana = mana
    """
    session_id: int
    
    # Characteristics (4 suits)
    spades: int = Field(default=0, description="♠ Strength, melee combat, will, intimidation")
    hearts: int = Field(default=0, description="♥ Magic, magical defense, wisdom, communication")
    diamonds: int = Field(default=0, description="♦ Endurance, physical defense, charisma, trading")
    clubs: int = Field(default=0, description="♣ Agility, ranged combat, acrobatics, stealth")
    
    # Experience (auto-leveling, not shown to player)
    spades_xp: int = Field(default=0, description="At 10 XP → +1 spades, reset to 0")
    hearts_xp: int = Field(default=0, description="At 10 XP → +1 hearts, reset to 0")
    diamonds_xp: int = Field(default=0, description="At 10 XP → +1 diamonds, reset to 0")
    clubs_xp: int = Field(default=0, description="At 10 XP → +1 clubs, reset to 0")
    
    # State
    hp: int = Field(default=100)
    max_hp: int = Field(default=100)
    mana: int = Field(default=50)
    max_mana: int = Field(default=50)
    gold: int = Field(default=0)
    
    # Inventory
    inventory: List[Item] = Field(default_factory=list, description="Up to 20 items")
    equipped: Dict[str, bool] = Field(default_factory=dict, description="Equipped items map")
    
    created_at: int = Field(default=0)
    updated_at: int = Field(default=0)
    
    @property
    def average_stat(self) -> int:
        """Average of all 4 characteristics (used for enemy scaling)"""
        return (self.spades + self.hearts + self.diamonds + self.clubs) // 4
    
    def get_stat_by_suit(self, suit: Suit) -> int:
        """Get characteristic value by suit"""
        suit_map = {
            Suit.SPADES: self.spades,
            Suit.HEARTS: self.hearts,
            Suit.DIAMONDS: self.diamonds,
            Suit.CLUBS: self.clubs
        }
        return suit_map[suit]
    
    def get_xp_by_suit(self, suit: Suit) -> int:
        """Get XP value by suit"""
        xp_map = {
            Suit.SPADES: self.spades_xp,
            Suit.HEARTS: self.hearts_xp,
            Suit.DIAMONDS: self.diamonds_xp,
            Suit.CLUBS: self.clubs_xp
        }
        return xp_map[suit]
    
    def get_equipped_bonus(self, suit: Suit) -> int:
        """Calculate total bonus from equipped items for a suit"""
        bonus = 0
        for item in self.inventory:
            if item.equipped and item.suit == suit:
                bonus += item.bonus
        return bonus
    
    def get_total_stat(self, suit: Suit) -> int:
        """Get total stat including equipped items"""
        return self.get_stat_by_suit(suit) + self.get_equipped_bonus(suit)


class CardPair(BaseModel):
    """A pair of cards drawn for a turn"""
    pair_number: int = Field(..., description="1 or 2")
    cards: List[Card] = Field(..., description="Exactly 2 cards")
    
    class Config:
        arbitrary_types_allowed = True


class SpecialEvent(str, Enum):
    """Special events from cards (only in peaceful time)"""
    JACK_TWIST = "Валет: Неожиданный поворот или появление NPC"
    QUEEN_FEMALE = "Дама: Влияние женского персонажа/энергии"
    KING_MALE = "Король: Влияние мужского персонажа/энергии"
    DOUBLE_ACES = "Два туза: Божественный успех!"
    DOUBLE_TWOS = "Две двойки: Катастрофа!"

