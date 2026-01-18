"""
Card deck implementation for game mechanics.
Based on standard 52-card deck (no jokers).
"""
import random
from typing import List
from .models import Card, Suit


class CardDeck:
    """
    Standard 52-card deck (no jokers).
    
    Ranks:
    - 2-10: face value
    - Jack: 11
    - Queen: 12
    - King: 13
    - Ace: 15
    """
    
    # Rank values (skip 1 and 14, use 15 for Ace as per rules)
    RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
    SUITS = list(Suit)
    
    def __init__(self):
        """Initialize a full deck of 52 cards"""
        self.reset()
    
    def reset(self):
        """Reset to full 52-card deck and shuffle"""
        self.cards = []
        for suit in self.SUITS:
            for rank in self.RANKS:
                self.cards.append(Card(rank, suit))
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def draw(self, count: int = 1) -> List[Card]:
        """
        Draw cards from the deck.
        
        Args:
            count: Number of cards to draw
            
        Returns:
            List of drawn cards
            
        Note: If deck runs out, automatically resets and continues drawing
        """
        drawn = []
        for _ in range(count):
            if len(self.cards) == 0:
                self.reset()  # Auto-reset when deck is empty
            drawn.append(self.cards.pop())
        return drawn
    
    def draw_pairs(self, num_pairs: int = 2) -> List[List[Card]]:
        """
        Draw multiple pairs of cards.
        
        Args:
            num_pairs: Number of pairs to draw (default 2)
            
        Returns:
            List of pairs, where each pair is a list of 2 cards
        """
        pairs = []
        for _ in range(num_pairs):
            pairs.append(self.draw(2))
        return pairs
    
    @property
    def remaining(self) -> int:
        """Number of cards remaining in deck"""
        return len(self.cards)

