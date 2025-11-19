"""Stubbed ProBas provider."""
from __future__ import annotations

from ..models.bom import BOMItem
from .lci_provider_base import LCIProcessCandidate, LCIProvider


class ProBasProvider:
    """Simulated provider returning deterministic matches."""

    name = "ProBas"

    def find_candidates(self, item: BOMItem) -> list[LCIProcessCandidate]:
        classification = getattr(item, "classification_unspsc", None)
        dataset_id = f"prob_{item.material_code or classification or 'generic'}"
        rule_id = "prob-material-code" if item.material_code else "prob-classification"
        confidence = 0.9 if item.material_code else 0.6
        stage = "own_operations" if rule_id == "supplier_override" else "raw_materials"
        brightway_ref = {
            "database": "stub-probas",
            "code": dataset_id,
        }
        return [
            LCIProcessCandidate(
                provider=self.name,
                dataset_id=dataset_id,
                name=f"ProBas dataset for {item.description}",
                description="Stub dataset - replace with ProBas lookup",
                confidence_score=confidence,
                mapping_rule_id=rule_id,
                metadata={"match_basis": item.material_code or classification or "n/a"},
                life_cycle_stage=stage,
                brightway_reference=brightway_ref,
            )
        ]
