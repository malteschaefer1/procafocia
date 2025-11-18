"""Scenario domain models."""
from __future__ import annotations

from dataclasses import dataclass


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
