"""BOM routes."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from ..models.bom import BOMItem
from ..schemas.bom_schema import BOMItemSchema, BOMUploadResponse
from ..services.product_repository import ProductRepository

router = APIRouter(prefix="/bom", tags=["bom"])
_repository = ProductRepository()


@router.post("/upload", response_model=BOMUploadResponse)
def upload_bom(payload: list[BOMItemSchema]) -> BOMUploadResponse:
    if not payload:
        raise HTTPException(status_code=400, detail="BOM payload is empty")
    product_id = payload[0].product_id
    product = _repository.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    items = [BOMItem(**item.model_dump()) for item in payload]
    try:
        _repository.replace_bom(product_id, items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BOMUploadResponse(product_id=product_id, items=payload)


@router.get("/{product_id}", response_model=BOMUploadResponse)
def get_bom(product_id: str) -> BOMUploadResponse:
    product = _repository.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    bom_items = _repository.get_bom(product_id)
    items = [BOMItemSchema(**asdict(item)) for item in bom_items]
    return BOMUploadResponse(product_id=product_id, items=items)
