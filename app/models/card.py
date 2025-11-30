"""Card and Deck domain models."""
import random
from dataclasses import dataclass
from typing import List
from enum import Enum


class Suit(str, Enum):
    """Card suits."""
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Rank(str, Enum):
    """Card ranks."""
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


# Mapping of ranks to their base values
RANK_VALUES = {
    Rank.ACE: 11,  # Handled specially in score calculation
    Rank.TWO: 2,
    Rank.THREE: 3,
    Rank.FOUR: 4,
    Rank.FIVE: 5,
    Rank.SIX: 6,
    Rank.SEVEN: 7,
    Rank.EIGHT: 8,
    Rank.NINE: 9,
    Rank.TEN: 10,
    Rank.JACK: 10,
    Rank.QUEEN: 10,
    Rank.KING: 10,
}


@dataclass(frozen=True)
class Card:
    """Immutable card value object."""
    suit: Suit
    rank: Rank
    
    @property
    def value(self) -> int:
        """Get the base value of the card."""
        return RANK_VALUES[self.rank]
    
    @property
    def is_ace(self) -> bool:
        """Check if card is an ace."""
        return self.rank == Rank.ACE
    
    def to_dict(self) -> dict:
        """Convert card to dictionary for JSON serialization."""
        return {
            "suit": self.suit.value,
            "rank": self.rank.value,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Create card from dictionary."""
        return cls(
            suit=Suit(data["suit"]),
            rank=Rank(data["rank"])
        )
    
    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"


class Deck:
    """Standard 52-card deck."""
    
    def __init__(self):
        """Initialize and shuffle a new deck."""
        self._cards: List[Card] = []
        self._initialize_deck()
    
    def _initialize_deck(self):
        """Create a fresh shuffled deck."""
        self._cards = [
            Card(suit=suit, rank=rank)
            for suit in Suit
            for rank in Rank
        ]
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self._cards)
    
    def draw(self) -> Card:
        """Draw a card from the deck. Reinitialize if empty."""
        if not self._cards:
            self._initialize_deck()
        return self._cards.pop()
    
    @property
    def remaining(self) -> int:
        """Number of cards remaining in deck."""
        return len(self._cards)
