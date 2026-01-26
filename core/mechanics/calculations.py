"""
Game mechanics calculations.
Pure functions for checks, combat, and other game rules.
"""
from typing import List, Dict, Tuple, Optional
from .models import Card, Character, Suit


# =============================================================================
# THRESHOLDS
# =============================================================================

# Difficulty presets: (easy, normal, hard, very_hard)
DIFFICULTY_PRESETS = {
    "easy": (100, 140, 180, 220),      # Easier thresholds, step 40
    "normal": (100, 150, 200, 250),    # Default thresholds, step 50
    "hard": (140, 180, 220, 260),      # Harder thresholds, step 40
}


def calculate_thresholds(character: Character, difficulty: str = "normal") -> Dict[str, any]:
    """
    Calculate difficulty thresholds for all suits.

    Formula:
    - Threshold = Base + Average_Stat (NOT the specific stat!)
    - This makes specialized characters better at their specialty

    Args:
        character: The character
        difficulty: "easy", "normal", or "hard" - affects base thresholds

    Returns:
        Dict with average and thresholds for each suit
    """
    average = character.average_stat

    # Get difficulty preset
    preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS["normal"])
    base_easy, base_normal, base_hard, base_very_hard = preset

    result = {"average": average, "difficulty": difficulty}

    for suit in Suit:
        # Thresholds use AVERAGE stat, not specific stat
        # This way specialized characters have advantage in their area
        result[suit.name.lower()] = {
            "easy": base_easy + average,
            "normal": base_normal + average,
            "hard": base_hard + average,
            "very_hard": base_very_hard + average
        }

    return result


# =============================================================================
# CARD BONUSES
# =============================================================================

def calculate_card_bonus(card: Card, action_suit: Suit) -> int:
    """
    Calculate bonus for a single card in combat.
    
    Priority (per tabletop rules):
    1. If suit matches action → +20
    2. Else if color matches action → +10
    3. Else → 0
    
    Args:
        card: The card
        action_suit: The suit of the action (e.g., SPADES for melee attack)
        
    Returns:
        Bonus value (0, 10, or 20)
    """
    # Priority 1: Suit match
    if card.suit == action_suit:
        return 20
    
    # Priority 2: Color match (card color matches action suit color)
    action_color = "red" if action_suit in [Suit.HEARTS, Suit.DIAMONDS] else "black"
    if card.color == action_color:
        return 10
    
    # No bonus
    return 0


# =============================================================================
# CHECKS (out of combat)
# =============================================================================

def calculate_check_for_pair(
    cards: List[Card],
    character: Character,
    suit: Suit
) -> Dict[str, any]:
    """
    Calculate check result for a pair of cards and a specific suit.
    
    Formula (per tabletop rules):
    - Each card: rank × 10
    - Bonus: +20 if suit matches OR +10 if color matches (not both!)
    - Total = card1_value + card2_value + character_stat
    
    Args:
        cards: Pair of cards (must be exactly 2)
        character: Character performing the check
        suit: Which characteristic to use
        
    Returns:
        Dict with calculation details
    """
    assert len(cards) == 2, "Must provide exactly 2 cards"
    
    card1, card2 = cards
    
    # Calculate each card separately
    def calc_card_value(card: Card, check_suit: Suit) -> tuple[int, int]:
        """Returns (base_value, bonus)"""
        base = card.rank * 10
        bonus = 0
        
        # +20 for suit match, OR +10 for color match (suit takes precedence)
        if card.suit == check_suit:
            bonus = 20
        elif card.color == ("red" if check_suit in [Suit.HEARTS, Suit.DIAMONDS] else "black"):
            bonus = 10
        
        return base, bonus
    
    card1_base, card1_bonus = calc_card_value(card1, suit)
    card2_base, card2_bonus = calc_card_value(card2, suit)
    
    card1_total = card1_base + card1_bonus
    card2_total = card2_base + card2_bonus
    
    # Character stat (including equipped bonuses)
    stat_value = character.get_total_stat(suit)
    
    # Total
    total = card1_total + card2_total + stat_value
    
    return {
        "cards": [str(card1), str(card2)],
        "card1": {"base": card1_base, "bonus": card1_bonus, "total": card1_total},
        "card2": {"base": card2_base, "bonus": card2_bonus, "total": card2_total},
        "stat_value": stat_value,
        "total": total
    }


def calculate_all_checks(
    card_pairs: List[List[Card]],
    character: Character,
    thresholds: Dict[str, any]
) -> Dict[str, any]:
    """
    Calculate all possible checks for all pairs and all suits.
    
    Args:
        card_pairs: List of card pairs (each pair is 2 cards)
        character: Character
        thresholds: Pre-calculated thresholds
        
    Returns:
        Dict with results for each pair and each suit
    """
    results = {}
    
    for idx, pair in enumerate(card_pairs, start=1):
        pair_key = f"pair_{idx}"
        pair_results = {
            "cards": [str(card) for card in pair]
        }
        
        # Calculate for each suit
        for suit in Suit:
            check_result = calculate_check_for_pair(pair, character, suit)
            suit_key = suit.name.lower()
            
            # Add threshold comparisons
            suit_thresholds = thresholds[suit_key]
            check_result["vs_thresholds"] = {}
            for difficulty, threshold in suit_thresholds.items():
                success = check_result["total"] >= threshold
                margin = check_result["total"] - threshold
                check_result["vs_thresholds"][difficulty] = {
                    "threshold": threshold,
                    "success": success,
                    "margin": margin
                }
            
            pair_results[suit_key] = check_result
        
        results[pair_key] = pair_results
    
    return results


# =============================================================================
# COMBAT
# =============================================================================

def calculate_combat_action(
    cards: List[Card],
    character: Character,
    action_suit: Suit
) -> Dict[str, any]:
    """
    Calculate combat action value for a pair of cards.
    
    Formula:
    - Card value = rank × 10
    - Each card gets bonus: +20 if suit matches, or +10 if both same color
    - Total = (card1_value + card1_bonus) + (card2_value + card2_bonus) + character_stat
    
    Args:
        cards: Pair of cards (must be exactly 2)
        character: Character
        action_suit: Suit of the action (SPADES for melee, CLUBS for ranged, etc.)
        
    Returns:
        Dict with calculation details
    """
    assert len(cards) == 2, "Must provide exactly 2 cards"
    
    card1, card2 = cards
    
    # Calculate bonuses (each card independently)
    card1_bonus = calculate_card_bonus(card1, action_suit)
    card2_bonus = calculate_card_bonus(card2, action_suit)
    
    # Card values
    card1_value = card1.value  # rank × 10
    card2_value = card2.value
    
    # Total card contribution
    cards_total = (card1_value + card1_bonus) + (card2_value + card2_bonus)
    
    # Character stat
    stat_value = character.get_total_stat(action_suit)
    
    # Final total
    total = cards_total + stat_value
    
    return {
        "cards": [str(card1), str(card2)],
        "card1_value": card1_value,
        "card1_bonus": card1_bonus,
        "card2_value": card2_value,
        "card2_bonus": card2_bonus,
        "cards_total": cards_total,
        "stat_value": stat_value,
        "total": total
    }


def calculate_all_combat_options(
    card_pairs: List[List[Card]],
    character: Character
) -> Dict[str, any]:
    """
    Calculate all possible combat actions for all pairs.
    
    For each pair, calculate:
    - Melee attack (SPADES)
    - Ranged attack (CLUBS)
    - Magic attack (HEARTS)
    - Physical defense (DIAMONDS)
    - Magic defense (HEARTS)
    - Combos (attack + defense with same cards)
    
    Args:
        card_pairs: List of card pairs
        character: Character
        
    Returns:
        Dict with all combat options for each pair
    """
    results = {}
    
    for idx, pair in enumerate(card_pairs, start=1):
        pair_key = f"pair_{idx}"
        
        # Calculate each action type
        melee = calculate_combat_action(pair, character, Suit.SPADES)
        ranged = calculate_combat_action(pair, character, Suit.CLUBS)
        magic_atk = calculate_combat_action(pair, character, Suit.HEARTS)
        phys_def = calculate_combat_action(pair, character, Suit.DIAMONDS)
        magic_def = calculate_combat_action(pair, character, Suit.HEARTS)
        
        # Combos (use same cards for both actions)
        combos = {
            "melee_and_phys_def": {
                "attack": melee["total"],
                "defense": phys_def["total"]
            },
            "ranged_and_phys_def": {
                "attack": ranged["total"],
                "defense": phys_def["total"]
            },
            "magic_and_phys_def": {
                "attack": magic_atk["total"],
                "defense": phys_def["total"]
            },
            "melee_and_magic_def": {
                "attack": melee["total"],
                "defense": magic_def["total"]
            }
        }
        
        # Check for combo failure (both red cards = attack fails)
        both_red = all(card.color == "red" for card in pair)
        if both_red:
            for combo_name in combos:
                combos[combo_name]["attack_failed"] = True
                combos[combo_name]["reason"] = "Обе карты красные - атака провалена"
        
        results[pair_key] = {
            "cards": [str(card) for card in pair],
            "melee_attack": melee,
            "ranged_attack": ranged,
            "magic_attack": magic_atk,
            "physical_defense": phys_def,
            "magic_defense": magic_def,
            "combos": combos
        }
    
    return results


# =============================================================================
# SPECIAL EVENTS
# =============================================================================

def detect_special_events(cards: List[Card]) -> List[str]:
    """
    Detect special events from cards.
    
    Only applies in PEACEFUL time, only for PLAYER.
    
    Special events:
    - Jack: Unexpected plot twist or NPC appearance
    - Queen: Female character/energy influence
    - King: Male character/energy influence
    - Two Aces: Divine success
    - Two Twos: Catastrophe
    
    Args:
        cards: List of all cards drawn this turn
        
    Returns:
        List of special event messages
    """
    events = []
    
    # Check for faces
    for card in cards:
        if card.face_meaning:
            events.append(f"{card}: {card.face_meaning}")
    
    # Check for double aces
    aces = [card for card in cards if card.rank == 15]
    if len(aces) >= 2:
        events.append("⚡ Два туза: Божественный успех!")
    
    # Check for double twos
    twos = [card for card in cards if card.rank == 2]
    if len(twos) >= 2:
        events.append("💀 Две двойки: Катастрофа!")
    
    return events


# =============================================================================
# CHARACTER CREATION
# =============================================================================

def calculate_starting_stats(cards: List[Card], assignments: Dict[str, int]) -> Dict[str, int]:
    """
    Calculate starting character stats from 5 cards.
    
    Formula: rank × 5 + (10 if suit matches)
    
    Args:
        cards: 5 cards drawn for character creation
        assignments: Map of suit name to card index (0-4)
                    Example: {"spades": 0, "hearts": 1, "diamonds": 2, "clubs": 3}
                    The 5th card (worst) is discarded
        
    Returns:
        Dict with stat values: {"spades": 45, "hearts": 70, ...}
    """
    stats = {}
    
    for suit_name, card_idx in assignments.items():
        card = cards[card_idx]
        suit = Suit[suit_name.upper()]
        
        # Base value
        value = card.rank * 5
        
        # Bonus if suit matches
        if card.suit == suit:
            value += 10
        
        stats[suit_name] = value
    
    return stats


def calculate_starting_hp_mana(stats: Dict[str, int]) -> Tuple[int, int, int, int]:
    """
    Calculate starting HP and mana from stats.
    
    Formula:
    - mana = hearts × 3
    - max_hp = spades + diamonds + clubs
    - hp = max_hp
    - max_mana = mana
    
    Args:
        stats: Character stats dict
        
    Returns:
        Tuple of (hp, max_hp, mana, max_mana)
    """
    mana = stats["hearts"] * 3
    max_hp = stats["spades"] + stats["diamonds"] + stats["clubs"]
    
    return (max_hp, max_hp, mana, mana)

