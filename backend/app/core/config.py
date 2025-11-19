"""Application configuration utilities."""
from __future__ import annotations

import os
from functools import lru_cache
from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Basic runtime settings with environment overrides."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    database_url: str = "sqlite:///./procafocia.db"
    mapping_min_similarity_for_candidate: float = 0.6
    mapping_min_similarity_for_auto_accept: float = 0.85
    soda4lca_base_url: str = ""
    soda4lca_username: str | None = None
    soda4lca_password: str | None = None
    soda4lca_token: str | None = None
    soda4lca_cache_dir: str = "cache/soda4lca"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    base = Settings(_env_file=Settings.model_config["env_file"])
    overrides = {}
    for field in Settings.model_fields:
        env_key = field.upper()
        if env_key in os.environ:
            overrides[field] = os.environ[env_key]
    if overrides:
        merged = base.model_dump()
        merged.update(overrides)
        return Settings(**merged)
    return base
