"""Application configuration utilities."""
from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    """Basic runtime settings with environment overrides."""

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings(_env_file=Settings.Config.env_file)
