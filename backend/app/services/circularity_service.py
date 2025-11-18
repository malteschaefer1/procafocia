"""Circularity orchestration service."""
from __future__ import annotations

from ..engines.circularity_engine_base import CircularityEngine
from ..models.bom import BOMItem
from ..models.product import Product
from ..models.results import ResultSet
from ..models.scenario import Scenario


class CircularityService:
    """Coordinates PCI calculations."""

    def __init__(self, engine: CircularityEngine):
        self.engine = engine

    def run(self, product: Product, bom: list[BOMItem], scenario: Scenario) -> ResultSet:
        circularity_result = self.engine.calculate_pci(product, bom, scenario)
        return ResultSet(
            id="result-circularity-demo",
            product_id=product.id,
            scenario_id=scenario.id,
            method_profile_id=scenario.method_profile_id,
            pcf_total_kg_co2e=0.0,
            pcf_breakdown={},
            circularity_indicators={
                "pci": circularity_result.pci_score,
                "sub_indicators": circularity_result.sub_indicators,
                "notes": circularity_result.notes,
            },
            provenance={"engine": "Bracquene2020CircularityEngine"},
        )
