"""PCF run endpoints."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..data_providers.boavizta_provider import BoaviztaProvider
from ..data_providers.probas_provider import ProBasProvider
from ..engines.pcf_engine_brightway import BrightwayPCFEngine
from ..models.method_profile import PCFMethodID
from ..schemas.method_profile_schema import MethodProfileListResponse, MethodProfileSchema
from ..schemas.results_schema import ResultSetSchema
from ..services.mapping_repository import MappingRepository
from ..services.mapping_service import MappingService
from ..services.pcf_service import PCFService
from ..services.product_repository import ProductRepository
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/pcf", tags=["pcf"])
_pcf_service = PCFService(engine=BrightwayPCFEngine())
_mapping_repository = MappingRepository()
_mapping_service = MappingService.from_settings(
    providers=[ProBasProvider(), BoaviztaProvider()],
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

    mapping_log = _mapping_service.map_bom(bom, scenario)
    result_set = _pcf_service.run(product=product, bom=bom, scenario=scenario, method_profile=method_profile)
    result_set.provenance["mapping_log"] = [
        {
            "item_id": entry.item_id,
            "selected": asdict(entry.selected) if entry.selected else None,
            "alternatives": [asdict(alt) for alt in entry.alternatives],
            "reasoning": entry.reasoning,
            "rule_applied": entry.rule_applied,
            "auto_selected": entry.auto_selected,
            "override_applied": entry.override_applied,
            "confidence_score": entry.confidence_score,
        }
        for entry in mapping_log
    ]

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
