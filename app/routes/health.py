"""Health check and metrics routes."""
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import get_settings
from app.services.metrics_service import get_metrics
from app.models.database import Player, GameSession, GameStatus

router = APIRouter(tags=["monitoring"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring.
    Returns application status and database connectivity.
    """
    settings = get_settings()
    metrics = get_metrics()
    
    # Check database connectivity
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "uptime_seconds": round(metrics.get_uptime(), 2)
    }


@router.get("/metrics")
async def get_application_metrics(db: Session = Depends(get_db)):
    """
    Get application metrics in JSON format.
    """
    metrics = get_metrics()
    
    # Get database stats
    total_players = db.query(Player).count()
    active_games = db.query(GameSession).filter(
        GameSession.status == GameStatus.IN_PROGRESS.value
    ).count()
    
    metrics_data = metrics.to_dict()
    metrics_data["active_games"] = active_games
    metrics_data["total_players"] = total_players
    
    return metrics_data


@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics(db: Session = Depends(get_db)):
    """
    Get application metrics in Prometheus format.
    """
    metrics = get_metrics()
    
    # Get database stats
    total_players = db.query(Player).count()
    active_games = db.query(GameSession).filter(
        GameSession.status == GameStatus.IN_PROGRESS.value
    ).count()
    
    prometheus_output = metrics.get_prometheus_format()
    
    # Add database metrics
    prometheus_output += f"\n\n# HELP blackjack_active_games Number of games in progress"
    prometheus_output += f"\n# TYPE blackjack_active_games gauge"
    prometheus_output += f"\nblackjack_active_games {active_games}"
    prometheus_output += f"\n\n# HELP blackjack_total_players Total registered players"
    prometheus_output += f"\n# TYPE blackjack_total_players counter"
    prometheus_output += f"\nblackjack_total_players {total_players}"
    
    return prometheus_output


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 only if the application is ready to serve traffic.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}, 503


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes/container orchestration.
    Simple check that the application process is running.
    """
    return {"status": "alive"}
