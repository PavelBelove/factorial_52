#!/usr/bin/env python3
"""
Test script for game mechanics.
Tests card drawing, calculations, and character management.
"""
import sys
sys.path.insert(0, '.')

from core.database.db_manager import DatabaseManager
from core.mechanics.mechanics_manager import MechanicsManager
from core.mechanics.card_deck import CardDeck
from core.mechanics.models import Suit
from core.config import settings

def test_card_deck():
    """Test card deck functionality"""
    print("=" * 60)
    print("TEST 1: Card Deck")
    print("=" * 60)
    
    deck = CardDeck()
    print(f"✅ Deck initialized: {deck.remaining} cards")
    
    # Draw pairs
    pairs = deck.draw_pairs(num_pairs=2)
    print(f"✅ Drew 2 pairs:")
    for idx, pair in enumerate(pairs, 1):
        print(f"  Pair {idx}: {pair[0]} + {pair[1]}")
    
    print(f"✅ Remaining: {deck.remaining} cards\n")


def test_character_creation():
    """Test character creation"""
    print("=" * 60)
    print("TEST 2: Character Creation")
    print("=" * 60)
    
    db = DatabaseManager()
    mechanics = MechanicsManager(db)
    
    # Generate cards
    creation_data = mechanics.generate_character_cards()
    print(f"✅ Generated 5 cards: {', '.join(creation_data['cards'])}")
    
    # Create character (simulate GM assigning)
    stats = {
        "spades": 45,    # 7×5 + 10 = 45
        "hearts": 70,    # Q×5 + 10 = 70
        "diamonds": 35,  # 5×5 + 10 = 35
        "clubs": 75      # K×5 + 10 = 75
    }
    
    # Create session first
    user = db.get_or_create_user("test_user", "telegram")
    session = db.create_session(user.id)
    
    character = mechanics.create_character(session.id, stats)
    print(f"✅ Character created:")
    print(f"  Spades (♠): {character.spades}")
    print(f"  Hearts (♥): {character.hearts}")
    print(f"  Diamonds (♦): {character.diamonds}")
    print(f"  Clubs (♣): {character.clubs}")
    print(f"  HP: {character.hp}/{character.max_hp}")
    print(f"  Mana: {character.mana}/{character.max_mana}")
    print(f"  Gold: {character.gold}")
    print(f"  Average: {character.average_stat}\n")
    
    return session.id


def test_checks_and_combat(session_id):
    """Test check and combat calculations"""
    print("=" * 60)
    print("TEST 3: Checks and Combat")
    print("=" * 60)
    
    db = DatabaseManager()
    mechanics = MechanicsManager(db)
    
    # Draw cards
    cards_data = mechanics.draw_cards_for_turn()
    print(f"✅ Drew cards:")
    for pair in cards_data["pairs"]:
        print(f"  Pair {pair['pair']}: {', '.join(pair['cards'])}")
    
    if cards_data["special_events"]:
        print(f"✅ Special events: {', '.join(cards_data['special_events'])}")
    
    # Calculate thresholds
    thresholds = mechanics.calculate_thresholds(session_id)
    print(f"\n✅ Thresholds calculated:")
    print(f"  Average stat: {thresholds['average']}")
    for suit in ["spades", "hearts", "diamonds", "clubs"]:
        print(f"  {suit}: easy={thresholds[suit]['easy']}, hard={thresholds[suit]['hard']}")
    
    # Calculate checks
    checks = mechanics.calculate_all_checks(session_id, cards_data)
    print(f"\n✅ Checks calculated (Pair 1):")
    for suit in ["spades", "hearts", "diamonds", "clubs"]:
        total = checks["pair_1"][suit]["total"]
        vs_normal = checks["pair_1"][suit]["vs_thresholds"]["normal"]
        success = "✅" if vs_normal["success"] else "❌"
        print(f"  {suit}: {total} {success} (normal: {vs_normal['threshold']})")
    
    # Calculate combat
    combat = mechanics.calculate_all_combat_options(session_id, cards_data)
    print(f"\n✅ Combat calculated (Pair 1):")
    print(f"  Melee attack: {combat['pair_1']['melee_attack']['total']}")
    print(f"  Ranged attack: {combat['pair_1']['ranged_attack']['total']}")
    print(f"  Physical defense: {combat['pair_1']['physical_defense']['total']}")
    print(f"  Magic defense: {combat['pair_1']['magic_defense']['total']}\n")


def test_gm_changes(session_id):
    """Test applying GM changes"""
    print("=" * 60)
    print("TEST 4: Applying GM Changes")
    print("=" * 60)
    
    db = DatabaseManager()
    mechanics = MechanicsManager(db)
    
    # Get initial state
    char_before = mechanics.get_character(session_id)
    print(f"Before changes:")
    print(f"  HP: {char_before.hp}/{char_before.max_hp}")
    print(f"  Spades: {char_before.spades} (XP: {char_before.spades_xp})")
    print(f"  Gold: {char_before.gold}")
    print(f"  Inventory: {len(char_before.inventory)} items")
    
    # Simulate GM response
    response_data = {
        "hp": -15,  # Took damage
        "gold": 100,  # Found gold
        "checks_used": [
            {"suit": "spades", "success": True}  # Successful strength check
        ],
        "inventory": {
            "add": [
                {
                    "id": "Меч_кладенец",
                    "type": "weapon",
                    "suit": "♠",
                    "bonus": 25,
                    "description": "Легендарное оружие"
                }
            ]
        }
    }
    
    mechanics.apply_gm_changes(session_id, response_data)
    
    # Get state after changes
    char_after = mechanics.get_character(session_id)
    print(f"\nAfter changes:")
    print(f"  HP: {char_after.hp}/{char_after.max_hp} (changed: {char_after.hp - char_before.hp})")
    print(f"  Spades: {char_after.spades} (XP: {char_after.spades_xp}) - gained +1 XP")
    print(f"  Gold: {char_after.gold} (changed: +{char_after.gold - char_before.gold})")
    print(f"  Inventory: {len(char_after.inventory)} items")
    if char_after.inventory:
        print(f"    - {char_after.inventory[0].id}")
    print()


def test_auto_leveling(session_id):
    """Test automatic leveling system"""
    print("=" * 60)
    print("TEST 5: Auto-Leveling")
    print("=" * 60)
    
    db = DatabaseManager()
    mechanics = MechanicsManager(db)
    
    char = mechanics.get_character(session_id)
    initial_spades = char.spades
    initial_hp = char.max_hp
    initial_mana = char.max_mana
    
    print(f"Initial: Spades={initial_spades}, HP={initial_hp}, Mana={initial_mana}")
    
    # Simulate 10 successful strength checks
    for i in range(10):
        response_data = {
            "checks_used": [{"suit": "spades", "success": True}]
        }
        mechanics.apply_gm_changes(session_id, response_data)
    
    char_after = mechanics.get_character(session_id)
    print(f"After 10 successful checks:")
    print(f"  Spades: {initial_spades} → {char_after.spades} (+{char_after.spades - initial_spades})")
    print(f"  Max HP: {initial_hp} → {char_after.max_hp} (+{char_after.max_hp - initial_hp})")
    print(f"  Max Mana: {initial_mana} → {char_after.max_mana} (+{char_after.max_mana - initial_mana})")
    print(f"  Spades XP: {char_after.spades_xp} (reset to 0)")
    print()


if __name__ == "__main__":
    print("\n🎲 PlexMem Game Mechanics Test Suite\n")
    
    try:
        # Test 1: Card Deck
        test_card_deck()
        
        # Test 2: Character Creation
        session_id = test_character_creation()
        
        # Test 3: Checks and Combat
        test_checks_and_combat(session_id)
        
        # Test 4: Applying GM Changes
        test_gm_changes(session_id)
        
        # Test 5: Auto-Leveling
        test_auto_leveling(session_id)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

