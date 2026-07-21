"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the FastAPI backend."""

    app_name: str = "Spinozah AI Education API"
    environment: str = "development"
    debug: bool = False
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/spinozah"
    )
    jwt_secret: str = "dev-only-change-me-use-secrets-token-urlsafe"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Build settings from the process environment."""
    return Settings()
