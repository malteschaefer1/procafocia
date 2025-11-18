"""Scenario creation/listing service."""
from __future__ import annotations

from ..models.method_profile import MethodProfile, MethodStandard
from ..models.scenario import Scenario
from .scenario_repository import ScenarioRepository


class ScenarioService:
    """Provides scenario + method profile definitions backed by persistence."""

    def __init__(self, repository: ScenarioRepository | None = None) -> None:
        self.repository = repository or ScenarioRepository()
        self.method_profiles = {
            "iso-basic": MethodProfile(
                id="iso-basic",
                name="ISO 14067 Basic",
                standard=MethodStandard.ISO14067,
                boundary="cradle-to-gate",
                allocation_rules="physical",
                recycling_handling="cut-off",
                cut_off_rules="1% mass or energy",
            ),
            "pact-pcf": MethodProfile(
                id="pact-pcf",
                name="PACT PCF",
                standard=MethodStandard.PACT,
                boundary="cradle-to-grave",
                allocation_rules="market-based",
                recycling_handling="avoidance",
                cut_off_rules="none",
            ),
        }

    def list_method_profiles(self) -> list[MethodProfile]:
        return list(self.method_profiles.values())

    def list_scenarios(self) -> list[Scenario]:
        return self.repository.list_scenarios()

    def get_method_profile(self, method_id: str) -> MethodProfile:
        return self.method_profiles[method_id]

    def get_scenario(self, scenario_id: str) -> Scenario:
        return self.repository.get_scenario(scenario_id)
