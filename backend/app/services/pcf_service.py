"""PCF orchestration service."""
from __future__ import annotations

from ..engines.pcf_engine_base import LCIModel, PCFEngine, PCFResult
from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.product import Product
from ..models.results import ResultSet
from ..models.scenario import Scenario


class PCFService:
    """Runs PCF calculations using a configured engine."""

    def __init__(self, engine: PCFEngine):
        self.engine = engine

    def run(
        self,
        product: Product,
        bom: list[BOMItem],
        scenario: Scenario,
        method_profile: MethodProfile,
        lci_model: LCIModel | None = None,
    ) -> ResultSet:
        pcf_result: PCFResult = self.engine.calculate_pcf(
            product=product,
            bom_items=bom,
            scenario=scenario,
            method_profile=method_profile,
            lci_model=lci_model,
        )
        result_set = ResultSet(
            id="result-pcf-demo",
            product_id=product.id,
            scenario_id=scenario.id,
            method_profile_id=method_profile.id.value,
            pcf_total_kg_co2e=pcf_result.total_kg_co2e,
            pcf_breakdown={"by_item": pcf_result.breakdown_by_item, "by_stage": pcf_result.breakdown_by_stage},
            circularity_indicators={},
            provenance={
                "engine": "BrightwayPCFEngine",
                "method_profile": {
                    "id": method_profile.id.value,
                    "name": method_profile.name,
                    "system_boundary": method_profile.system_boundary,
                },
                "notes": ["Stub results, replace with real Brightway calculations"],
            },
        )
        return result_set
