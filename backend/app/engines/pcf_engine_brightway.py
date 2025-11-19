"""Brightway2-based PCF engine stubs."""
from __future__ import annotations

from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.product import Product
from ..models.scenario import Scenario
from .pcf_engine_base import LCIEntry, LCIModel, PCFEngine, PCFResult


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

        entries: list[LCIEntry] = []
        for item in bom:
            classification = getattr(item, "classification_unspsc", None)
            entries.append(
                LCIEntry(
                    bom_item_id=item.id,
                    dataset_id=f"stub-process-{item.material_code or classification}",
                    provider="stub",
                    quantity=item.quantity,
                    unit=item.unit or "ea",
                    mass_kg=item.mass_kg,
                    life_cycle_stage="raw_materials",
                    brightway_reference={"database": "stub", "code": item.id},
                    metadata={"notes": "TODO: fetch dataset from Brightway and align units"},
                )
            )
        return LCIModel(bom_items=bom, entries=entries)

    def calculate_pcf(
        self,
        product: Product,
        bom_items: list[BOMItem],
        scenario: Scenario,
        method_profile: MethodProfile,
        lci_model: LCIModel | None = None,
    ) -> PCFResult:
        """Run a Brightway LCA and summarize PCF results."""

        if lci_model is None:
            lci_model = self.map_bom_to_lci(bom_items, scenario)
        # TODO: Build Brightway demand vector using `lci_model` data.
        # TODO: Execute LCI + LCIA steps with the selected method profile.
        total = sum(entry.mass_kg * 1.5 for entry in lci_model.entries)  # placeholder factor
        breakdown_by_item = {}
        for entry in lci_model.entries:
            breakdown_by_item[entry.bom_item_id] = breakdown_by_item.get(entry.bom_item_id, 0.0) + entry.mass_kg * 1.5
        breakdown_by_stage = {
            "materials": total * 0.6,
            "manufacturing": total * 0.3,
            "distribution": total * 0.1,
        }
        provenance = {
            "pcf_method_id": method_profile.id.value,
            "pcf_method_name": method_profile.name,
            "system_boundary": method_profile.system_boundary,
            "notes": "Placeholder Brightway2 calculation; currently cradle-to-gate regardless of method.",
        }
        if method_profile.system_boundary == "cradle_to_grave":
            provenance["todo"] = "Model use phase and end-of-life flows for cradle-to-grave methods."
        return PCFResult(
            total_kg_co2e=total,
            breakdown_by_item=breakdown_by_item,
            breakdown_by_stage=breakdown_by_stage,
            provenance=provenance,
        )
