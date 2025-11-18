"""Circularity endpoints."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..engines.circularity_engine_pci_bracquene2020 import Bracquene2020CircularityEngine
from ..schemas.pci_result_schema import PCIResultSchema
from ..schemas.results_schema import ResultSetSchema
from ..services.circularity_service import CircularityService
from ..services.product_repository import ProductRepository
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/circularity", tags=["circularity"])
_circularity_service = CircularityService(Bracquene2020CircularityEngine())
_product_repository = ProductRepository()
_scenario_service = ScenarioService()


class CircularityRunRequest(BaseModel):
    product_id: str
    scenario_id: str = "default"


@router.post("/run", response_model=ResultSetSchema)
def run_circularity(request: CircularityRunRequest) -> ResultSetSchema:
    product, bom = _get_product_and_bom(request.product_id)
    scenario = _get_scenario_or_404(request.scenario_id)
    result_set = _circularity_service.run(product=product, bom=bom, scenario=scenario)
    return ResultSetSchema(**result_set.__dict__)


@router.get("/pci/{product_id}", response_model=PCIResultSchema)
def get_pci(product_id: str, scenario_id: str = "default") -> PCIResultSchema:
    product, bom = _get_product_and_bom(product_id)
    scenario = _get_scenario_or_404(scenario_id)
    pci_result = _circularity_service.calculate_pci(product, bom, scenario)
    data = asdict(pci_result)
    return PCIResultSchema(**data)


def _get_product_and_bom(product_id: str):
    product = _product_repository.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    bom = _product_repository.get_bom(product_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not uploaded for product")
    return product, bom


def _get_scenario_or_404(scenario_id: str):
    try:
        return _scenario_service.get_scenario(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
