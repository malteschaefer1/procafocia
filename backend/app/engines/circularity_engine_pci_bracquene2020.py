"""PCI implementation scaffold following Bracquene et al. (2020)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models.bom import BOMItem
from ..models.product import Product
from ..models.scenario import Scenario
from .circularity_engine_base import CircularityEngine, CircularityResult


@dataclass
class PCIInputs:
    """Structured inputs required by Bracquene 2020 equations."""

    virgin_mass: float
    recycled_mass: float
    reused_mass: float
    remanufactured_mass: float
    mass_to_recycling: float
    mass_to_landfill: float
    mass_to_incineration: float
    lifetime_years: float | None = None


class Bracquene2020CircularityEngine(CircularityEngine):
    """Mirrors equations from Bracquene et al. (2020).

    Doc references:
        - Sec. 3.2 Mass Flow Model
        - Sec. 4 PCI calculation & weighting
        - Eq. (1)-(6) for recycling/reuse contributions
    """

    def calculate_pci(self, product: Product, bom: list[BOMItem], scenario: Scenario, pci_profile: dict | None = None) -> CircularityResult:
        pci_inputs = self._aggregate_inputs(bom)
        sub_indicators = self._calculate_sub_indicators(pci_inputs, pci_profile)
        # TODO: Replace weighted sum with exact formulation from Bracquene 2020.
        pci_score = sum(sub_indicators.values()) / max(len(sub_indicators), 1)
        notes = [
            "TODO: Plug in exact PCI formula (Bracquene 2020 Eq. 8)",
            "Inputs aggregated assuming BOM mass is in kg",
        ]
        return CircularityResult(pci_score=pci_score, sub_indicators=sub_indicators, notes=notes)

    def _aggregate_inputs(self, bom: Iterable[BOMItem]) -> PCIInputs:
        virgin = recycled = reused = reman = to_recycling = to_landfill = to_incineration = 0.0
        for item in bom:
            mass = item.mass_kg * item.quantity
            recycled_share = item.recycled_content_share or 0
            reused_share = item.reused_share or 0
            reman_share = item.remanufactured_share or 0
            recyclability_rate = item.recyclability_rate or 0
            landfill_rate = item.landfill_rate or 0
            incineration_rate = item.incineration_rate or 0

            virgin += mass * (1 - recycled_share - reused_share)
            recycled += mass * recycled_share
            reused += mass * reused_share
            reman += mass * reman_share
            to_recycling += mass * recyclability_rate
            to_landfill += mass * landfill_rate
            to_incineration += mass * incineration_rate

        return PCIInputs(
            virgin_mass=virgin,
            recycled_mass=recycled,
            reused_mass=reused,
            remanufactured_mass=reman,
            mass_to_recycling=to_recycling,
            mass_to_landfill=to_landfill,
            mass_to_incineration=to_incineration,
        )

    def _calculate_sub_indicators(self, inputs: PCIInputs, profile: dict | None) -> dict[str, float]:
        profile = profile or {}
        sub_scores: dict[str, float] = {}
        # TODO: Implement exact contributions following MCI/PCI equation mapping
        sub_scores["recycled_content"] = inputs.recycled_mass / max(inputs.virgin_mass + inputs.recycled_mass, 1e-6)
        sub_scores["reused_content"] = inputs.reused_mass / max(inputs.virgin_mass + inputs.reused_mass, 1e-6)
        sub_scores["end_of_life_recycling"] = inputs.mass_to_recycling / max(
            inputs.mass_to_recycling + inputs.mass_to_landfill + inputs.mass_to_incineration, 1e-6
        )
        return sub_scores
