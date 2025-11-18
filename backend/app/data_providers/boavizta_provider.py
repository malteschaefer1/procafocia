"""Stubbed Boavizta provider."""
from __future__ import annotations

from ..models.bom import BOMItem
from .lci_provider_base import LCIProcessCandidate, LCIProvider


class BoaviztaProvider:
    """Simplified provider that performs fuzzy matching by description."""

    name = "Boavizta"

    def find_candidates(self, item: BOMItem) -> list[LCIProcessCandidate]:
        score = 0.5
        if "aluminum" in item.description.lower():
            score = 0.8
        return [
            LCIProcessCandidate(
                provider=self.name,
                dataset_id=f"boa_{item.id}",
                name=f"Boavizta guess for {item.description}",
                description="Fuzzy match placeholder",
                confidence_score=score,
                mapping_rule_id="boa-fuzzy-description",
                metadata={"heuristic": "description_contains_aluminum"},
            )
        ]
