"""Domain model for products."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """Represents a product definition for PCF/PCI assessments."""

    id: str
    name: str
    version: str
    functional_unit: str
    lifetime_years: Optional[float] = None
    use_profile: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)
