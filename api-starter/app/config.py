# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Application configuration loaded from environment variables."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Application
    APP_NAME: str = "API Starter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./api_starter.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-env-file"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
