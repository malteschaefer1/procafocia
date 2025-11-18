"""PCF orchestration service."""
from __future__ import annotations

from ..engines.pcf_engine_base import PCFEngine, PCFResult
from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.results import ResultSet
from ..models.scenario import Scenario


class PCFService:
    """Runs PCF calculations using a configured engine."""

    def __init__(self, engine: PCFEngine):
        self.engine = engine

    def run(self, bom: list[BOMItem], scenario: Scenario, method_profile: MethodProfile) -> ResultSet:
        lci_model = self.engine.map_bom_to_lci(bom, scenario)
        pcf_result: PCFResult = self.engine.calculate_pcf(lci_model, scenario, method_profile)
        result_set = ResultSet(
            id="result-pcf-demo",
            product_id=bom[0].product_id if bom else "unknown",
            scenario_id=scenario.id,
            method_profile_id=method_profile.id,
            pcf_total_kg_co2e=pcf_result.total_kg_co2e,
            pcf_breakdown={"by_item": pcf_result.breakdown_by_item, "by_stage": pcf_result.breakdown_by_stage},
            circularity_indicators={},
            provenance={
                "engine": "BrightwayPCFEngine",
                "notes": ["Stub results, replace with real Brightway calculations"],
            },
        )
        return result_set
