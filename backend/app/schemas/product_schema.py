"""Pydantic schemas for product resources."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    id: str
    name: str
    version: str
    functional_unit: str
    lifetime_years: float | None = None
    use_profile: str | None = None


class ProductResponse(ProductCreate):
    """Response schema extending creation fields."""

    metadata: dict[str, str] = Field(default_factory=dict)
