"""LCI provider interface definitions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models.bom import BOMItem


@dataclass
class LCIProcessCandidate:
    """Result candidate from provider queries."""

    provider: str
    dataset_id: str
    name: str
    description: str
    confidence_score: float
    mapping_rule_id: str
    metadata: dict[str, str]
    life_cycle_stage: str | None = None
    brightway_reference: dict | None = None


class LCIProvider(Protocol):
    """Protocol that LCI providers must implement."""

    name: str

    def find_candidates(self, item: BOMItem) -> list[LCIProcessCandidate]:
        """Return potential process matches for a BOM item."""

        raise NotImplementedError
