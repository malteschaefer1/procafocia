"""BOM routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.bom import BOMItem
from ..schemas.bom_schema import BOMItemSchema, BOMUploadResponse
from ..services import state

router = APIRouter(prefix="/bom", tags=["bom"])


@router.post("/upload", response_model=BOMUploadResponse)
def upload_bom(payload: list[BOMItemSchema]) -> BOMUploadResponse:
    if not payload:
        raise HTTPException(status_code=400, detail="BOM payload is empty")
    product_id = payload[0].product_id
    state.boms[product_id] = [BOMItem(**item.dict()) for item in payload]
    return BOMUploadResponse(product_id=product_id, items=payload)


@router.get("/{product_id}", response_model=BOMUploadResponse)
def get_bom(product_id: str) -> BOMUploadResponse:
    if product_id not in state.boms:
        raise HTTPException(status_code=404, detail="BOM not found")
    items = [BOMItemSchema(**item.__dict__) for item in state.boms[product_id]]
    return BOMUploadResponse(product_id=product_id, items=items)
