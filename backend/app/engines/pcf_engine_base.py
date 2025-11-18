"""PCF engine abstractions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.scenario import Scenario


@dataclass
class LCIModel:
    """Placeholder for a life-cycle inventory representation."""

    bom_items: list[BOMItem]
    mappings: list[dict]


@dataclass
class PCFResult:
    """Represents PCF computation results."""

    total_kg_co2e: float
    breakdown_by_item: dict[str, float]
    breakdown_by_stage: dict[str, float]


class PCFEngine(Protocol):
    """Interface for PCF engines."""

    def map_bom_to_lci(self, bom: list[BOMItem], scenario: Scenario) -> LCIModel:
        raise NotImplementedError

    def calculate_pcf(self, lci_model: LCIModel, scenario: Scenario, method_profile: MethodProfile) -> PCFResult:
        raise NotImplementedError
