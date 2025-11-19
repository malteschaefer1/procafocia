"""Schemas for mapping history and overrides."""
from __future__ import annotations

from pydantic import BaseModel


class MappingCandidateSchema(BaseModel):
    provider: str
    dataset_id: str
    name: str | None = None
    description: str | None = None
    confidence_score: float | None = None
    mapping_rule_id: str | None = None
    metadata: dict | None = None
    life_cycle_stage: str | None = None
    brightway_reference: dict | None = None


class MappingDecisionSchema(BaseModel):
    item_id: str
    selected: MappingCandidateSchema | None
    alternatives: list[MappingCandidateSchema]
    reasoning: str
    rule_applied: str | None
    auto_selected: bool
    override_applied: bool
    confidence_score: float | None
    life_cycle_stage: str | None = None
    candidates: list[MappingCandidateSchema] | None = None


class MappingHistorySchema(BaseModel):
    id: int
    product_id: str
    bom_item_id: str
    scenario_id: str | None
    selected_dataset_id: str | None
    selected_provider: str | None
    confidence_score: float | None
    rule_applied: str | None
    user_id: str | None
    comment: str | None
    auto_selected: bool
    is_override: bool
    created_at: str
    life_cycle_stage: str | None = None


class MappingOverrideRequest(BaseModel):
    product_id: str
    bom_item_id: str
    dataset_id: str
    provider: str
    user_id: str | None = None
    comment: str | None = None
    scenario_id: str | None = None
    life_cycle_stage: str | None = None
