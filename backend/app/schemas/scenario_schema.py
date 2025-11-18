"""Scenario schemas."""
from __future__ import annotations

from pydantic import BaseModel


class ScenarioSchema(BaseModel):
    id: str
    name: str
    goal_scope: str
    system_boundary: str
    geography: str
    method_profile_id: str
    energy_mix_profile: str
    end_of_life_model: str
