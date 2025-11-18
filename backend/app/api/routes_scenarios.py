"""Scenario + method profile routes."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas.method_profile_schema import MethodProfileSchema
from ..schemas.scenario_schema import ScenarioSchema
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
_service = ScenarioService()


@router.get("", response_model=list[ScenarioSchema])
def list_scenarios() -> list[ScenarioSchema]:
    return [ScenarioSchema(**scenario.__dict__) for scenario in _service.list_scenarios()]


@router.get("/methods", response_model=list[MethodProfileSchema])
def list_method_profiles() -> list[MethodProfileSchema]:
    return [MethodProfileSchema(**profile.__dict__) for profile in _service.list_method_profiles()]
