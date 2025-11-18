"""PCF run endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..data_providers.boavizta_provider import BoaviztaProvider
from ..data_providers.probas_provider import ProBasProvider
from ..engines.pcf_engine_brightway import BrightwayPCFEngine
from ..schemas.results_schema import ResultSetSchema
from ..services import state
from ..services.mapping_service import MappingService
from ..services.pcf_service import PCFService
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/pcf", tags=["pcf"])
_pcf_service = PCFService(engine=BrightwayPCFEngine())
_mapping_service = MappingService(providers=[ProBasProvider(), BoaviztaProvider()])
_scenario_service = ScenarioService()


class PCFRunRequest(BaseModel):
    product_id: str
    scenario_id: str = "default"


@router.post("/run", response_model=ResultSetSchema)
def run_pcf(request: PCFRunRequest) -> ResultSetSchema:
    if request.product_id not in state.boms:
        raise HTTPException(status_code=404, detail="BOM not uploaded for product")
    if request.product_id not in state.products:
        raise HTTPException(status_code=404, detail="Product not found")

    bom = state.boms[request.product_id]
    scenario = _scenario_service.get_scenario(request.scenario_id)
    method_profile = _scenario_service.get_method_profile(scenario.method_profile_id)

    mapping_log = _mapping_service.map_bom(bom, scenario)
    result_set = _pcf_service.run(bom=bom, scenario=scenario, method_profile=method_profile)
    result_set.provenance["mapping_log"] = [entry.__dict__ for entry in mapping_log]

    return ResultSetSchema(**result_set.__dict__)
