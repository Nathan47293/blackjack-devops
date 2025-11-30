"""Routes module."""
from app.routes.game import router as game_router
from app.routes.health import router as health_router

__all__ = ["game_router", "health_router"]
