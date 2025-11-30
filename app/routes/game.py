"""Game API routes."""
from fastapi import APIRouter, Depends, Cookie, Response
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.services.game_service import GameService
from app.services.metrics_service import get_metrics

router = APIRouter(prefix="/api", tags=["game"])


def get_session_id(session_id: Optional[str] = Cookie(default=None)) -> str:
    """Get or create session ID from cookie."""
    return session_id or str(uuid.uuid4())


@router.post("/start-game")
async def start_game(
    bet: int,
    response: Response,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """Start a new game with the specified bet."""
    metrics = get_metrics()
    metrics.increment_request("/api/start-game")
    
    # Set session cookie
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    service = GameService(db)
    game, error = service.start_game(session_id, bet)
    
    if error:
        metrics.increment_error()
        return {"error": error}
    
    player = service.get_or_create_player(session_id)
    return service.get_game_state(game, player)


@router.post("/hit")
async def hit(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """Player requests another card."""
    metrics = get_metrics()
    metrics.increment_request("/api/hit")
    
    service = GameService(db)
    game, error = service.hit(session_id)
    
    if error:
        metrics.increment_error()
        return {"error": error}
    
    player = service.get_or_create_player(session_id)
    return service.get_game_state(game, player)


@router.post("/stand")
async def stand(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """Player stands, dealer plays."""
    metrics = get_metrics()
    metrics.increment_request("/api/stand")
    
    service = GameService(db)
    game, error = service.stand(session_id)
    
    if error:
        metrics.increment_error()
        return {"error": error}
    
    player = service.get_or_create_player(session_id)
    return service.get_game_state(game, player)


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """Get player statistics."""
    metrics = get_metrics()
    metrics.increment_request("/api/stats")
    
    service = GameService(db)
    stats = service.get_player_stats(session_id)
    
    if not stats:
        return {"error": "Player not found"}
    
    return stats


@router.post("/reset")
async def reset_balance(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """Reset player balance to initial amount."""
    metrics = get_metrics()
    metrics.increment_request("/api/reset")
    
    service = GameService(db)
    player = service.reset_player(session_id)
    
    return {"balance": player.balance, "message": "Balance reset successfully"}
