"""Tests for Card and Deck models."""
import pytest
from app.models.card import Card, Deck, Suit, Rank, RANK_VALUES


class TestCard:
    """Test cases for Card class."""
    
    def test_card_creation(self):
        """Test creating a card."""
        card = Card(suit=Suit.HEARTS, rank=Rank.ACE)
        assert card.suit == Suit.HEARTS
        assert card.rank == Rank.ACE
    
    def test_card_value_ace(self):
        """Test ace value."""
        card = Card(suit=Suit.SPADES, rank=Rank.ACE)
        assert card.value == 11
    
    def test_card_value_face_cards(self):
        """Test face card values."""
        jack = Card(suit=Suit.HEARTS, rank=Rank.JACK)
        queen = Card(suit=Suit.DIAMONDS, rank=Rank.QUEEN)
        king = Card(suit=Suit.CLUBS, rank=Rank.KING)
        
        assert jack.value == 10
        assert queen.value == 10
        assert king.value == 10
    
    def test_card_value_number_cards(self):
        """Test number card values."""
        two = Card(suit=Suit.SPADES, rank=Rank.TWO)
        five = Card(suit=Suit.HEARTS, rank=Rank.FIVE)
        ten = Card(suit=Suit.DIAMONDS, rank=Rank.TEN)
        
        assert two.value == 2
        assert five.value == 5
        assert ten.value == 10
    
    def test_card_is_ace(self):
        """Test ace detection."""
        ace = Card(suit=Suit.HEARTS, rank=Rank.ACE)
        king = Card(suit=Suit.HEARTS, rank=Rank.KING)
        
        assert ace.is_ace is True
        assert king.is_ace is False
    
    def test_card_to_dict(self):
        """Test card serialization."""
        card = Card(suit=Suit.HEARTS, rank=Rank.KING)
        card_dict = card.to_dict()
        
        assert card_dict["suit"] == "♥"
        assert card_dict["rank"] == "K"
        assert card_dict["value"] == 10
    
    def test_card_from_dict(self):
        """Test card deserialization."""
        data = {"suit": "♠", "rank": "A"}
        card = Card.from_dict(data)
        
        assert card.suit == Suit.SPADES
        assert card.rank == Rank.ACE
    
    def test_card_string_representation(self):
        """Test card string representation."""
        card = Card(suit=Suit.DIAMONDS, rank=Rank.QUEEN)
        assert str(card) == "Q♦"
    
    def test_card_immutability(self):
        """Test that cards are immutable."""
        card = Card(suit=Suit.HEARTS, rank=Rank.ACE)
        with pytest.raises(AttributeError):
            card.suit = Suit.SPADES


class TestDeck:
    """Test cases for Deck class."""
    
    def test_deck_creation(self):
        """Test creating a deck."""
        deck = Deck()
        assert deck.remaining == 52
    
    def test_deck_draw(self):
        """Test drawing a card."""
        deck = Deck()
        card = deck.draw()
        
        assert isinstance(card, Card)
        assert deck.remaining == 51
    
    def test_deck_draw_all_cards(self):
        """Test drawing all cards from deck."""
        deck = Deck()
        cards = [deck.draw() for _ in range(52)]
        
        assert len(cards) == 52
        assert deck.remaining == 0
    
    def test_deck_auto_refill(self):
        """Test deck auto-refills when empty."""
        deck = Deck()
        
        # Draw all cards
        for _ in range(52):
            deck.draw()
        
        assert deck.remaining == 0
        
        # Drawing should refill the deck
        card = deck.draw()
        assert isinstance(card, Card)
        assert deck.remaining == 51
    
    def test_deck_contains_all_cards(self):
        """Test deck contains all 52 unique cards."""
        deck = Deck()
        cards = [deck.draw() for _ in range(52)]
        
        # Check we have exactly 4 of each rank
        rank_counts = {}
        for card in cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        for rank in Rank:
            assert rank_counts[rank] == 4
    
    def test_deck_shuffle(self):
        """Test deck shuffling produces different order."""
        deck1 = Deck()
        deck2 = Deck()
        
        cards1 = [deck1.draw() for _ in range(10)]
        cards2 = [deck2.draw() for _ in range(10)]
        
        # It's statistically improbable that two shuffled decks
        # have the same order (but possible, so we allow 2 matches)
        matches = sum(1 for c1, c2 in zip(cards1, cards2) 
                      if c1.suit == c2.suit and c1.rank == c2.rank)
        assert matches < 5  # Very unlikely to match more than 5


class TestRankValues:
    """Test RANK_VALUES mapping."""
    
    def test_all_ranks_have_values(self):
        """Test all ranks have defined values."""
        for rank in Rank:
            assert rank in RANK_VALUES
    
    def test_rank_values_correct(self):
        """Test rank values are correct."""
        assert RANK_VALUES[Rank.ACE] == 11
        assert RANK_VALUES[Rank.TWO] == 2
        assert RANK_VALUES[Rank.TEN] == 10
        assert RANK_VALUES[Rank.JACK] == 10
        assert RANK_VALUES[Rank.QUEEN] == 10
        assert RANK_VALUES[Rank.KING] == 10
