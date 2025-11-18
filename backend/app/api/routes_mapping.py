"""Mapping history and override routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..data_providers.boavizta_provider import BoaviztaProvider
from ..data_providers.probas_provider import ProBasProvider
from ..models.bom import BOMItem
from ..schemas.mapping_schema import (
    MappingDecisionSchema,
    MappingHistorySchema,
    MappingOverrideRequest,
    MappingCandidateSchema,
)
from ..services import state
from ..services.mapping_repository import MappingRepository
from ..services.mapping_service import MappingService
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/mapping", tags=["mapping"])
_repository = MappingRepository()
_mapping_service = MappingService.from_settings(
    providers=[ProBasProvider(), BoaviztaProvider()],
    repository=_repository,
)
_scenario_service = ScenarioService()


def _candidate_to_schema(candidate) -> MappingCandidateSchema:
    if candidate is None:
        return None
    return MappingCandidateSchema(**candidate.__dict__)


@router.get("/history/{product_id}", response_model=list[MappingHistorySchema])
def list_history(product_id: str) -> list[MappingHistorySchema]:
    with _repository.session() as session:
        entries = _repository.list_history_for_product(session, product_id)
        return [
            MappingHistorySchema(
                id=entry.id,
                product_id=entry.product_id,
                bom_item_id=entry.bom_item_id,
                scenario_id=entry.scenario_id,
                selected_dataset_id=entry.selected_dataset_id,
                selected_provider=entry.selected_provider,
                confidence_score=entry.confidence_score,
                rule_applied=entry.rule_applied,
                user_id=entry.user_id,
                comment=entry.comment,
                auto_selected=entry.auto_selected,
                is_override=entry.is_override,
                created_at=entry.created_at.isoformat(),
            )
            for entry in entries
        ]


@router.post("/override", response_model=MappingDecisionSchema)
def create_override(payload: MappingOverrideRequest) -> MappingDecisionSchema:
    product_bom = state.boms.get(payload.product_id)
    if not product_bom:
        raise HTTPException(status_code=404, detail="BOM not found for product")
    bom_item = _get_bom_item(product_bom, payload.bom_item_id)
    if not bom_item:
        raise HTTPException(status_code=404, detail="BOM item not found")
    scenario = None
    if payload.scenario_id:
        scenario = _scenario_service.get_scenario(payload.scenario_id)

    decision = _mapping_service.record_override(
        bom_item=bom_item,
        dataset_id=payload.dataset_id,
        provider=payload.provider,
        user_id=payload.user_id,
        comment=payload.comment,
        scenario=scenario,
    )

    return MappingDecisionSchema(
        item_id=decision.item_id,
        selected=_candidate_to_schema(decision.selected),
        alternatives=[_candidate_to_schema(alt) for alt in decision.alternatives],
        reasoning=decision.reasoning,
        rule_applied=decision.rule_applied,
        auto_selected=decision.auto_selected,
        override_applied=decision.override_applied,
        confidence_score=decision.confidence_score,
    )


def _get_bom_item(bom_items: list[BOMItem], bom_item_id: str) -> BOMItem | None:
    for item in bom_items:
        if item.id == bom_item_id:
            return item
    return None
