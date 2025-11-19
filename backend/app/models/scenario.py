"""Scenario domain models."""
from __future__ import annotations

from dataclasses import dataclass, field

from .pci import MaterialCircularityParameters
from .method_profile import PCFMethodID


@dataclass
class Scenario:
    """Represents a calculation scenario for PCF/PCI runs."""

    id: str
    name: str
    goal_scope: str
    system_boundary: str
    geography: str
    method_profile_id: str
    energy_mix_profile: str
    end_of_life_model: str
    pcf_method_id: PCFMethodID = PCFMethodID.PACT_V3
    collection_fraction_for_reuse: float = 0.0
    collection_fraction_for_recycling: float = 0.0
    utility_factor: float | None = None
    design_lifetime_functional_units: float | None = None
    actual_used_functional_units: float | None = None
    material_parameters: dict[str, MaterialCircularityParameters] = field(default_factory=dict)

    def compute_utility_factor(self) -> float:
        """Return utility factor using provided values or computed functional units."""

        if self.utility_factor and self.utility_factor > 0:
            return self.utility_factor
        if (
            self.design_lifetime_functional_units
            and self.actual_used_functional_units
            and self.design_lifetime_functional_units > 0
        ):
            return max(self.actual_used_functional_units / self.design_lifetime_functional_units, 1e-6)
        return 1.0
