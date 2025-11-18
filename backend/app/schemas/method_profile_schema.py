"""Method profile schemas."""
from __future__ import annotations

from pydantic import BaseModel

from ..models.method_profile import MethodStandard


class MethodProfileSchema(BaseModel):
    id: str
    name: str
    standard: MethodStandard
    boundary: str
    allocation_rules: str
    recycling_handling: str
    cut_off_rules: str
    notes: str | None = None
