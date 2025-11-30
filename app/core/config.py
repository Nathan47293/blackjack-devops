"""Application configuration using environment variables."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "Blackjack Game"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./blackjack.db"
    
    # Game settings
    initial_balance: int = 100
    min_bet: int = 1
    max_bet: int = 1000
    dealer_stand_threshold: int = 17
    blackjack_payout: float = 1.5
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
