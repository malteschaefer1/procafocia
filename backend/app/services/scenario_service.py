"""Scenario creation/listing service."""
from __future__ import annotations

from ..models.method_profile import MethodProfile, PCF_METHOD_PROFILES, PCFMethodID
from ..models.scenario import Scenario
from .scenario_repository import ScenarioRepository


class ScenarioService:
    """Provides scenario + method profile definitions backed by persistence."""

    def __init__(self, repository: ScenarioRepository | None = None) -> None:
        self.repository = repository or ScenarioRepository()

    def list_method_profiles(self) -> list[MethodProfile]:
        return list(PCF_METHOD_PROFILES.values())

    def list_scenarios(self) -> list[Scenario]:
        return self.repository.list_scenarios()

    def get_method_profile(self, method_id: str | PCFMethodID) -> MethodProfile:
        method_key = PCFMethodID(method_id)
        return PCF_METHOD_PROFILES[method_key]

    def get_scenario(self, scenario_id: str) -> Scenario:
        return self.repository.get_scenario(scenario_id)
