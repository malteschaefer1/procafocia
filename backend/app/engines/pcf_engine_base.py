"""PCF engine abstractions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.product import Product
from ..models.scenario import Scenario


@dataclass
class LCIEntry:
    """Represents a single dataset contribution to the LCI."""

    bom_item_id: str
    dataset_id: str
    provider: str
    quantity: float
    unit: str
    mass_kg: float
    life_cycle_stage: str
    brightway_reference: dict | None
    metadata: dict | None = None


@dataclass
class LCIModel:
    """Placeholder for a life-cycle inventory representation."""

    bom_items: list[BOMItem]
    entries: list[LCIEntry]


@dataclass
class PCFResult:
    """Represents PCF computation results."""

    total_kg_co2e: float
    breakdown_by_item: dict[str, float]
    breakdown_by_stage: dict[str, float]
    provenance: dict = field(default_factory=dict)


class PCFEngine(Protocol):
    """Interface for PCF engines."""

    def map_bom_to_lci(self, bom: list[BOMItem], scenario: Scenario) -> LCIModel:
        raise NotImplementedError

    def calculate_pcf(
        self,
        product: Product,
        bom_items: list[BOMItem],
        scenario: Scenario,
        method_profile: MethodProfile,
        lci_model: LCIModel | None = None,
    ) -> PCFResult:
        raise NotImplementedError
