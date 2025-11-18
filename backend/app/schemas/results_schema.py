"""Result schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ResultSetSchema(BaseModel):
    id: str
    product_id: str
    scenario_id: str
    method_profile_id: str
    pcf_total_kg_co2e: float
    pcf_breakdown: dict = Field(default_factory=dict)
    circularity_indicators: dict = Field(default_factory=dict)
    provenance: dict = Field(default_factory=dict)
