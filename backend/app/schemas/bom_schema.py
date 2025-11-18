"""Schemas for BOM resources."""
from __future__ import annotations

from pydantic import BaseModel


class BOMItemSchema(BaseModel):
    id: str
    product_id: str
    description: str
    classification: str | None = None
    material_code: str | None = None
    component_code: str | None = None
    mass_kg: float
    quantity: float
    origin_country: str | None = None
    manufacturing_location: str | None = None
    supplier_id: str | None = None
    recycled_content_share: float | None = None
    reused_share: float | None = None
    remanufactured_share: float | None = None
    recyclability_rate: float | None = None
    landfill_rate: float | None = None
    incineration_rate: float | None = None


class BOMUploadResponse(BaseModel):
    product_id: str
    items: list[BOMItemSchema]
