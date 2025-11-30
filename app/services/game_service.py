"""Game service containing blackjack business logic."""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.card import Card, Deck
from app.models.database import Player, GameSession, GameStatus
from app.core.config import get_settings


class ScoreCalculator:
    """Calculates hand scores with ace handling."""
    
    @staticmethod
    def calculate(cards: List[Card]) -> int:
        """
        Calculate the best score for a hand.
        Aces can be 1 or 11, choosing the best value.
        """
        score = 0
        aces = 0
        
        for card in cards:
            if card.is_ace:
                aces += 1
            else:
                score += card.value
        
        # Add aces, using 11 when possible without busting
        for _ in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
        
        return score
    
    @staticmethod
    def is_bust(score: int) -> bool:
        """Check if score is a bust (over 21)."""
        return score > 21
    
    @staticmethod
    def is_blackjack(cards: List[Card]) -> bool:
        """Check if hand is a natural blackjack (21 with 2 cards)."""
        if len(cards) != 2:
            return False
        return ScoreCalculator.calculate(cards) == 21


class GameService:
    """Service for managing blackjack game operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.score_calculator = ScoreCalculator()
    
    def get_or_create_player(self, session_id: str) -> Player:
        """Get existing player or create new one."""
        player = self.db.query(Player).filter(
            Player.session_id == session_id
        ).first()
        
        if not player:
            player = Player(
                session_id=session_id,
                balance=self.settings.initial_balance
            )
            self.db.add(player)
            self.db.commit()
            self.db.refresh(player)
        
        return player
    
    def get_active_game(self, player_id: int) -> Optional[GameSession]:
        """Get player's active game if one exists."""
        return self.db.query(GameSession).filter(
            GameSession.player_id == player_id,
            GameSession.status == GameStatus.IN_PROGRESS.value
        ).first()
    
    def start_game(self, session_id: str, bet: int) -> Tuple[GameSession, str]:
        """
        Start a new game for a player.
        Returns (game_session, error_message).
        """
        player = self.get_or_create_player(session_id)
        
        # Validate bet
        if bet < self.settings.min_bet:
            return None, f"Minimum bet is ${self.settings.min_bet}"
        if bet > self.settings.max_bet:
            return None, f"Maximum bet is ${self.settings.max_bet}"
        if bet > player.balance:
            return None, "Insufficient balance"
        
        # Check for existing active game
        active_game = self.get_active_game(player.id)
        if active_game:
            return None, "Game already in progress"
        
        # Deduct bet from balance
        player.balance -= bet
        
        # Create new deck and deal initial hands
        deck = Deck()
        player_hand = [deck.draw(), deck.draw()]
        dealer_hand = [deck.draw(), deck.draw()]
        
        # Calculate initial scores
        player_score = self.score_calculator.calculate(player_hand)
        dealer_score = self.score_calculator.calculate(dealer_hand)
        
        # Create game session
        game = GameSession(
            player_id=player.id,
            bet_amount=bet,
            player_hand=[card.to_dict() for card in player_hand],
            dealer_hand=[card.to_dict() for card in dealer_hand],
            deck_state=[card.to_dict() for card in deck._cards],
            player_score=player_score,
            dealer_score=dealer_score,
        )
        
        # Check for natural blackjack
        if self.score_calculator.is_blackjack(player_hand):
            if self.score_calculator.is_blackjack(dealer_hand):
                # Both have blackjack - push
                game.status = GameStatus.PUSH.value
                game.message = "Both have Blackjack! Push!"
                game.payout = bet
                player.balance += bet
                player.total_pushes += 1
            else:
                # Player blackjack wins
                game.status = GameStatus.BLACKJACK.value
                game.message = "Blackjack! You win!"
                payout = int(bet * (1 + self.settings.blackjack_payout))
                game.payout = payout
                player.balance += payout
                player.total_wins += 1
            
            game.completed_at = datetime.utcnow()
            player.total_games += 1
        
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        
        return game, ""
    
    def hit(self, session_id: str) -> Tuple[GameSession, str]:
        """
        Player draws a card.
        Returns (game_session, error_message).
        """
        player = self.get_or_create_player(session_id)
        game = self.get_active_game(player.id)
        
        if not game:
            return None, "No active game"
        
        # Reconstruct deck from state
        deck_cards = [Card.from_dict(c) for c in game.deck_state]
        
        if not deck_cards:
            return None, "Deck is empty"
        
        # Draw card
        new_card = deck_cards.pop()
        player_hand = [Card.from_dict(c) for c in game.player_hand]
        player_hand.append(new_card)
        
        # Update game state
        game.player_hand = [card.to_dict() for card in player_hand]
        game.deck_state = [card.to_dict() for card in deck_cards]
        game.player_score = self.score_calculator.calculate(player_hand)
        
        # Check for bust
        if self.score_calculator.is_bust(game.player_score):
            game.status = GameStatus.PLAYER_BUST.value
            game.message = "Bust! You lose!"
            game.completed_at = datetime.utcnow()
            player.total_games += 1
            player.total_losses += 1
        
        self.db.commit()
        self.db.refresh(game)
        
        return game, ""
    
    def stand(self, session_id: str) -> Tuple[GameSession, str]:
        """
        Player stands - dealer plays out their hand.
        Returns (game_session, error_message).
        """
        player = self.get_or_create_player(session_id)
        game = self.get_active_game(player.id)
        
        if not game:
            return None, "No active game"
        
        # Reconstruct hands and deck
        player_hand = [Card.from_dict(c) for c in game.player_hand]
        dealer_hand = [Card.from_dict(c) for c in game.dealer_hand]
        deck_cards = [Card.from_dict(c) for c in game.deck_state]
        
        # Dealer draws until reaching threshold
        dealer_score = self.score_calculator.calculate(dealer_hand)
        while dealer_score < self.settings.dealer_stand_threshold and deck_cards:
            dealer_hand.append(deck_cards.pop())
            dealer_score = self.score_calculator.calculate(dealer_hand)
        
        # Update game state
        game.dealer_hand = [card.to_dict() for card in dealer_hand]
        game.deck_state = [card.to_dict() for card in deck_cards]
        game.dealer_score = dealer_score
        
        player_score = game.player_score
        
        # Determine winner
        game.completed_at = datetime.utcnow()
        player.total_games += 1
        
        if self.score_calculator.is_bust(dealer_score):
            game.status = GameStatus.DEALER_BUST.value
            game.message = "Dealer busts! You win!"
            game.payout = game.bet_amount * 2
            player.balance += game.payout
            player.total_wins += 1
        elif dealer_score > player_score:
            game.status = GameStatus.DEALER_WIN.value
            game.message = "Dealer wins!"
            player.total_losses += 1
        elif dealer_score < player_score:
            game.status = GameStatus.PLAYER_WIN.value
            game.message = "You win!"
            game.payout = game.bet_amount * 2
            player.balance += game.payout
            player.total_wins += 1
        else:
            game.status = GameStatus.PUSH.value
            game.message = "Push!"
            game.payout = game.bet_amount
            player.balance += game.payout
            player.total_pushes += 1
        
        self.db.commit()
        self.db.refresh(game)
        
        return game, ""
    
    def get_game_state(self, game: GameSession, player: Player) -> dict:
        """Convert game session to API response format."""
        player_hand = game.player_hand
        
        # Hide dealer's hole card if game is in progress
        if game.status == GameStatus.IN_PROGRESS.value:
            dealer_hand = [
                game.dealer_hand[0],
                {"suit": "?", "rank": "?", "value": 0}
            ]
            dealer_score = game.dealer_hand[0]["value"]
        else:
            dealer_hand = game.dealer_hand
            dealer_score = game.dealer_score
        
        return {
            "playerHand": player_hand,
            "dealerHand": dealer_hand,
            "playerScore": game.player_score,
            "dealerScore": dealer_score,
            "balance": player.balance,
            "bet": game.bet_amount,
            "gameOver": game.status != GameStatus.IN_PROGRESS.value,
            "message": game.message
        }
    
    def get_player_stats(self, session_id: str) -> Optional[dict]:
        """Get player statistics."""
        player = self.db.query(Player).filter(
            Player.session_id == session_id
        ).first()
        
        if not player:
            return None
        
        win_rate = 0.0
        if player.total_games > 0:
            win_rate = player.total_wins / player.total_games * 100
        
        return {
            "balance": player.balance,
            "total_games": player.total_games,
            "total_wins": player.total_wins,
            "total_losses": player.total_losses,
            "total_pushes": player.total_pushes,
            "win_rate": round(win_rate, 2)
        }
    
    def reset_player(self, session_id: str) -> Player:
        """Reset player balance to initial amount."""
        player = self.get_or_create_player(session_id)
        player.balance = self.settings.initial_balance
        self.db.commit()
        self.db.refresh(player)
        return player
