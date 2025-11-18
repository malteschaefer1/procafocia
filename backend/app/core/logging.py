"""Logging setup helpers."""
from __future__ import annotations

import logging
from typing import Optional

from .config import get_settings


def configure_logging(level: Optional[str] = None) -> None:
    """Configure root logging for the service."""

    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, (level or settings.log_level).upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
