"""PCF run endpoints."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..data_providers.boavizta_provider import BoaviztaProvider
from ..data_providers.probas_provider import ProBasProvider
from ..data_providers.soda4lca_provider import Soda4LCAProvider
from ..engines.pcf_engine_brightway import BrightwayPCFEngine
from ..models.method_profile import PCFMethodID
from ..schemas.method_profile_schema import MethodProfileListResponse, MethodProfileSchema
from ..schemas.results_schema import ResultSetSchema
from ..services.mapping_repository import MappingRepository
from ..services.mapping_service import MappingDecision, MappingService
from ..services.pcf_service import PCFService
from ..services.product_repository import ProductRepository
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/pcf", tags=["pcf"])
_pcf_service = PCFService(engine=BrightwayPCFEngine())
_mapping_repository = MappingRepository()
_mapping_service = MappingService.from_settings(
    providers=[ProBasProvider(), BoaviztaProvider(), Soda4LCAProvider()],
    repository=_mapping_repository,
)
_product_repository = ProductRepository()
_scenario_service = ScenarioService()


class PCFRunRequest(BaseModel):
    product_id: str
    scenario_id: str = "default"
    pcf_method_id: PCFMethodID | None = None


@router.post("/run", response_model=ResultSetSchema)
def run_pcf(request: PCFRunRequest) -> ResultSetSchema:
    product = _product_repository.get_product(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    bom = _product_repository.get_bom(request.product_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not uploaded for product")

    scenario = _get_scenario_or_404(request.scenario_id)
    method_id = request.pcf_method_id or scenario.pcf_method_id
    method_profile = _scenario_service.get_method_profile(method_id)

    try:
        lci_model, decisions = _mapping_service.build_lci_model(product, bom, scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result_set = _pcf_service.run(
        product=product, bom=bom, scenario=scenario, method_profile=method_profile, lci_model=lci_model
    )
    result_set.provenance["mapping_log"] = [_decision_to_payload(decision) for decision in decisions]

    return ResultSetSchema(**result_set.__dict__)


@router.get("/methods", response_model=MethodProfileListResponse)
def list_pcf_methods() -> MethodProfileListResponse:
    methods = [MethodProfileSchema(**method.__dict__) for method in _scenario_service.list_method_profiles()]
    return MethodProfileListResponse(methods=methods)


def _get_scenario_or_404(scenario_id: str):
    try:
        return _scenario_service.get_scenario(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _decision_to_payload(decision: MappingDecision) -> dict:
    return {
        "item_id": decision.item_id,
        "selected": asdict(decision.selected) if decision.selected else None,
        "alternatives": [asdict(alt) for alt in decision.alternatives],
        "candidates": [asdict(candidate) for candidate in (decision.candidates or [])],
        "reasoning": decision.reasoning,
        "rule_applied": decision.rule_applied,
        "auto_selected": decision.auto_selected,
        "override_applied": decision.override_applied,
        "confidence_score": decision.confidence_score,
        "life_cycle_stage": decision.life_cycle_stage,
    }
