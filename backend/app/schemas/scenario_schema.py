"""Scenario schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class MaterialCircularityParametersSchema(BaseModel):
    material_key: str
    efficiency_feedstock_production: float
    efficiency_component_production: float
    recovered_fraction_feedstock_losses: float
    recovered_fraction_component_losses: float
    efficiency_material_separation_eol: float
    efficiency_recycled_feedstock_production: float
    notes: str | None = None


class ScenarioSchema(BaseModel):
    id: str
    name: str
    goal_scope: str
    system_boundary: str
    geography: str
    method_profile_id: str
    energy_mix_profile: str
    end_of_life_model: str
    collection_fraction_for_reuse: float = 0.0
    collection_fraction_for_recycling: float = 0.0
    utility_factor: float | None = None
    design_lifetime_functional_units: float | None = None
    actual_used_functional_units: float | None = None
    material_parameters: dict[str, MaterialCircularityParametersSchema] = Field(default_factory=dict)
