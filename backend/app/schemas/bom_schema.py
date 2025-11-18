"""Schemas for BOM resources."""
from __future__ import annotations

from pydantic import BaseModel


class BOMItemSchema(BaseModel):
    id: str
    product_id: str
    parent_bom_item_id: str | None = None
    description: str
    quantity: float
    unit: str | None = None
    mass_kg: float
    material_family: str | None = None
    material_code: str | None = None
    classification_unspsc: str | None = None
    supplier_id: str | None = None
    component_code: str | None = None
    recycled_content_share: float | None = None
    reused_share: float | None = None
    remanufactured_share: float | None = None
    recyclability_rate: float | None = None
    landfill_rate: float | None = None
    incineration_rate: float | None = None
    country_of_origin: str | None = None
    manufacturing_location: str | None = None
    lci_dataset_id: str | None = None


class BOMUploadResponse(BaseModel):
    product_id: str
    items: list[BOMItemSchema]
