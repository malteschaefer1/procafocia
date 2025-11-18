"""Scenario creation/listing service."""
from __future__ import annotations

from ..models.method_profile import MethodProfile, MethodStandard
from ..models.scenario import Scenario


class ScenarioService:
    """Provides in-memory scenario + method profile definitions."""

    def __init__(self) -> None:
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
        self.scenarios = {
            "default": Scenario(
                id="default",
                name="EU Reference",
                goal_scope="Cradle-to-gate PCF",
                system_boundary="cradle-to-gate",
                geography="EU",
                method_profile_id="iso-basic",
                energy_mix_profile="EU-avg",
                end_of_life_model="EU-2019",
            )
        }

    def list_method_profiles(self) -> list[MethodProfile]:
        return list(self.method_profiles.values())

    def list_scenarios(self) -> list[Scenario]:
        return list(self.scenarios.values())

    def get_method_profile(self, method_id: str) -> MethodProfile:
        return self.method_profiles[method_id]

    def get_scenario(self, scenario_id: str) -> Scenario:
        return self.scenarios[scenario_id]
