"""Scenario persistence helpers."""
from __future__ import annotations

import json
from typing import Callable

from sqlalchemy import select

from ..db.base import get_session
from ..db.models import ScenarioModel
from ..models.pci import MaterialCircularityParameters
from ..models.scenario import Scenario


class ScenarioRepository:
    def __init__(self, session_factory: Callable = get_session):
        self._session_factory = session_factory

    def list_scenarios(self) -> list[Scenario]:
        with self._session_factory() as session:
            results = session.scalars(select(ScenarioModel)).all()
            return [self._to_domain(model) for model in results]

    def get_scenario(self, scenario_id: str) -> Scenario:
        with self._session_factory() as session:
            model = session.get(ScenarioModel, scenario_id)
            if not model:
                raise ValueError(f"Scenario {scenario_id} not found")
            return self._to_domain(model)

    def _to_domain(self, model: ScenarioModel) -> Scenario:
        params_dict = json.loads(model.material_parameters or "{}")
        material_params = {
            key: MaterialCircularityParameters(**value)
            for key, value in params_dict.items()
        }
        return Scenario(
            id=model.id,
            name=model.name,
            goal_scope=model.goal_scope,
            system_boundary=model.system_boundary,
            geography=model.geography,
            method_profile_id=model.method_profile_id,
            energy_mix_profile=model.energy_mix_profile,
            end_of_life_model=model.end_of_life_model,
            collection_fraction_for_reuse=model.collection_fraction_for_reuse,
            collection_fraction_for_recycling=model.collection_fraction_for_recycling,
            utility_factor=model.utility_factor,
            design_lifetime_functional_units=model.design_lifetime_functional_units,
            actual_used_functional_units=model.actual_used_functional_units,
            material_parameters=material_params,
        )
