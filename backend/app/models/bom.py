"""Bill-of-materials domain models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BOMItem:
    """Represents a single BOM line enriched with circularity and mapping attributes."""

    id: str
    product_id: str
    parent_bom_item_id: Optional[str]
    description: str
    quantity: float
    unit: Optional[str]
    mass_kg: float
    material_family: Optional[str]
    material_code: Optional[str]
    classification_unspsc: Optional[str]
    supplier_id: Optional[str]
    component_code: Optional[str] = None
    recycled_content_share: Optional[float] = None
    reused_share: Optional[float] = None
    remanufactured_share: Optional[float] = None
    recyclability_rate: Optional[float] = None
    landfill_rate: Optional[float] = None
    incineration_rate: Optional[float] = None
    country_of_origin: Optional[str] = None
    manufacturing_location: Optional[str] = None
    lci_dataset_id: Optional[str] = None
