"""Method profile schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..models.method_profile import MethodStandard, PCFMethodID


class MethodProfileSchema(BaseModel):
    id: PCFMethodID
    name: str
    short_description: str
    reference_url: str
    standard: MethodStandard
    system_boundary: str
    life_cycle_stages_included: list[str]
    ghg_aggregation_method: str | None = None
    pcf_output_schema: str | None = None
    data_priority_hierarchy: list[str] | None = None
    requires_dqr_scoring: bool = False
    notes: str | None = None


class MethodProfileListResponse(BaseModel):
    methods: list[MethodProfileSchema] = Field(default_factory=list)
