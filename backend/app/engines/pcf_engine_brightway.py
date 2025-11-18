"""Brightway2-based PCF engine stubs."""
from __future__ import annotations

from typing import Any

from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.scenario import Scenario
from .pcf_engine_base import LCIModel, PCFEngine, PCFResult


class BrightwayPCFEngine(PCFEngine):
    """Outlines how Brightway2 would be orchestrated.

    The heavy lifting (database loading, LCA execution) is intentionally omitted.
    Replace TODO sections with real brightway2 code when data and methods are available.
    """

    def __init__(self, project_name: str = "procafocia-demo") -> None:
        self.project_name = project_name
        self._ensure_project_initialized()

    def _ensure_project_initialized(self) -> None:
        """Connect to or create a Brightway2 project.

        TODO: integrate `brightway2` and perform `projects.set_current` etc.
        """

        # Placeholder for initialization logic.
        self._bw_project_ready = True

    def map_bom_to_lci(self, bom: list[BOMItem], scenario: Scenario) -> LCIModel:
        """Convert BOM information into an LCI model structure."""

        mappings: list[dict[str, Any]] = []
        for item in bom:
            mappings.append(
                {
                    "item_id": item.id,
                    "process_key": f"stub-process-{item.material_code or item.classification}",
                    "quantity": item.quantity,
                    "mass_kg": item.mass_kg,
                    "notes": "TODO: fetch dataset from Brightway and align units",
                }
            )
        return LCIModel(bom_items=bom, mappings=mappings)

    def calculate_pcf(self, lci_model: LCIModel, scenario: Scenario, method_profile: MethodProfile) -> PCFResult:
        """Run a Brightway LCA and summarize PCF results."""

        # TODO: Build Brightway demand vector using `lci_model` data.
        # TODO: Execute LCI + LCIA steps with the selected method profile.
        total = sum(item.mass_kg * 1.5 for item in lci_model.bom_items)  # placeholder factor
        breakdown_by_item = {item.id: item.mass_kg * 1.5 for item in lci_model.bom_items}
        breakdown_by_stage = {
            "materials": total * 0.6,
            "manufacturing": total * 0.3,
            "distribution": total * 0.1,
        }
        return PCFResult(total_kg_co2e=total, breakdown_by_item=breakdown_by_item, breakdown_by_stage=breakdown_by_stage)
