"""Circularity endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..engines.circularity_engine_pci_bracquene2020 import Bracquene2020CircularityEngine
from ..schemas.results_schema import ResultSetSchema
from ..services import state
from ..services.circularity_service import CircularityService
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/circularity", tags=["circularity"])
_circularity_service = CircularityService(Bracquene2020CircularityEngine())
_scenario_service = ScenarioService()


class CircularityRunRequest(BaseModel):
    product_id: str
    scenario_id: str = "default"


@router.post("/run", response_model=ResultSetSchema)
def run_circularity(request: CircularityRunRequest) -> ResultSetSchema:
    if request.product_id not in state.products:
        raise HTTPException(status_code=404, detail="Product not found")
    if request.product_id not in state.boms:
        raise HTTPException(status_code=404, detail="BOM not uploaded for product")

    product = state.products[request.product_id]
    bom = state.boms[request.product_id]
    scenario = _scenario_service.get_scenario(request.scenario_id)

    result_set = _circularity_service.run(product=product, bom=bom, scenario=scenario)
    return ResultSetSchema(**result_set.__dict__)
