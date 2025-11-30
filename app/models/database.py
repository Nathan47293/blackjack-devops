"""Database models for game persistence."""
import json
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class GameStatus(str, Enum):
    """Game session status."""
    IN_PROGRESS = "in_progress"
    PLAYER_WIN = "player_win"
    DEALER_WIN = "dealer_win"
    PUSH = "push"
    PLAYER_BUST = "player_bust"
    DEALER_BUST = "dealer_bust"
    BLACKJACK = "blackjack"


class Player(Base):
    """Player model for tracking user data."""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    balance = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to game sessions
    games = relationship("GameSession", back_populates="player")
    
    # Statistics
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    total_pushes = Column(Integer, default=0)


class GameSession(Base):
    """Individual game session."""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    bet_amount = Column(Integer, nullable=False)
    status = Column(String(20), default=GameStatus.IN_PROGRESS.value)
    
    # Store hands as JSON
    player_hand = Column(JSON, default=list)
    dealer_hand = Column(JSON, default=list)
    
    # Deck state (remaining cards)
    deck_state = Column(JSON, default=list)
    
    # Scores
    player_score = Column(Integer, default=0)
    dealer_score = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Result
    payout = Column(Integer, default=0)
    message = Column(String(100), default="")
    
    # Relationship
    player = relationship("Player", back_populates="games")
    
    @property
    def is_game_over(self) -> bool:
        """Check if game is finished."""
        return self.status != GameStatus.IN_PROGRESS.value
