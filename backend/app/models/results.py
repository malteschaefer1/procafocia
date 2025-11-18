"""Results domain model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultSet:
    """Captures PCF + PCI results with provenance metadata."""

    id: str
    product_id: str
    scenario_id: str
    method_profile_id: str
    pcf_total_kg_co2e: float
    pcf_breakdown: dict[str, Any] = field(default_factory=dict)
    circularity_indicators: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
