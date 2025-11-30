"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CardSchema(BaseModel):
    """Card representation for API responses."""
    suit: str
    rank: str
    value: int


class StartGameRequest(BaseModel):
    """Request to start a new game."""
    bet: int = Field(..., gt=0, description="Bet amount must be positive")


class GameStateResponse(BaseModel):
    """Response containing current game state."""
    player_hand: List[CardSchema] = Field(alias="playerHand")
    dealer_hand: List[CardSchema] = Field(alias="dealerHand")
    player_score: int = Field(alias="playerScore")
    dealer_score: int = Field(alias="dealerScore")
    balance: int
    bet: int
    game_over: bool = Field(alias="gameOver")
    message: str
    
    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Error response."""
    error: str


class PlayerStats(BaseModel):
    """Player statistics."""
    balance: int
    total_games: int
    total_wins: int
    total_losses: int
    total_pushes: int
    win_rate: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    database: str
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """Metrics response."""
    request_count: int
    error_count: int
    active_games: int
    total_players: int
    avg_response_time_ms: float
