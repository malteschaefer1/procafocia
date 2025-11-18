"""Bill-of-materials domain models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BOMItem:
    """Represents a single BOM line enriched with circularity attributes."""

    id: str
    product_id: str
    description: str
    classification: Optional[str]
    material_code: Optional[str]
    component_code: Optional[str]
    mass_kg: float
    quantity: float
    origin_country: Optional[str] = None
    manufacturing_location: Optional[str] = None
    supplier_id: Optional[str] = None
    recycled_content_share: Optional[float] = None
    reused_share: Optional[float] = None
    remanufactured_share: Optional[float] = None
    recyclability_rate: Optional[float] = None
    landfill_rate: Optional[float] = None
    incineration_rate: Optional[float] = None
