"""Mapping history and override routes."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from ..data_providers.boavizta_provider import BoaviztaProvider
from ..data_providers.probas_provider import ProBasProvider
from ..models.bom import BOMItem
from ..schemas.mapping_schema import (
    MappingCandidateSchema,
    MappingDecisionSchema,
    MappingHistorySchema,
    MappingOverrideRequest,
)
from ..services.mapping_repository import MappingRepository
from ..services.mapping_service import MappingService
from ..services.product_repository import ProductRepository
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/mapping", tags=["mapping"])
_repository = MappingRepository()
_product_repository = ProductRepository()
_mapping_service = MappingService.from_settings(
    providers=[ProBasProvider(), BoaviztaProvider()],
    repository=_repository,
)
_scenario_service = ScenarioService()


def _candidate_to_schema(candidate) -> MappingCandidateSchema:
    if candidate is None:
        return None
    return MappingCandidateSchema(**candidate.__dict__)


def _model_to_decision_schema(model) -> MappingDecisionSchema:
    payload = json.loads(model.decision_payload) if model.decision_payload else {}
    alternatives = [MappingCandidateSchema(**alt) for alt in payload.get("alternatives", [])]
    selected = None
    if model.selected_dataset_id:
        selected = MappingCandidateSchema(
            provider=model.selected_provider,
            dataset_id=model.selected_dataset_id,
            confidence_score=model.confidence_score,
            mapping_rule_id=model.rule_applied,
            metadata={"decision_id": model.id},
        )
    return MappingDecisionSchema(
        item_id=model.bom_item_id,
        selected=selected,
        alternatives=alternatives,
        reasoning=payload.get("reasoning", ""),
        rule_applied=model.rule_applied,
        auto_selected=model.auto_selected,
        override_applied=model.is_override,
        confidence_score=model.confidence_score,
    )


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


@router.get("/review/{product_id}", response_model=list[MappingDecisionSchema])
def review_mapping(product_id: str, scenario_id: str = "default") -> list[MappingDecisionSchema]:
    product = _product_repository.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    bom = _product_repository.get_bom(product_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not uploaded for product")
    scenario = _get_scenario_or_404(scenario_id)

    with _repository.session() as session:
        existing = _repository.latest_decisions_for_product(session, product_id)

    if existing:
        return [_model_to_decision_schema(entry) for entry in existing]

    mapping_log = _mapping_service.map_bom(bom, scenario)
    return [
        MappingDecisionSchema(
            item_id=decision.item_id,
            selected=_candidate_to_schema(decision.selected),
            alternatives=[_candidate_to_schema(alt) for alt in decision.alternatives],
            reasoning=decision.reasoning,
            rule_applied=decision.rule_applied,
            auto_selected=decision.auto_selected,
            override_applied=decision.override_applied,
            confidence_score=decision.confidence_score,
        )
        for decision in mapping_log
    ]


@router.post("/override", response_model=MappingDecisionSchema)
def create_override(payload: MappingOverrideRequest) -> MappingDecisionSchema:
    bom_items = _product_repository.get_bom(payload.product_id)
    if not bom_items:
        raise HTTPException(status_code=404, detail="BOM not found for product")
    bom_item = _get_bom_item(bom_items, payload.bom_item_id)
    if not bom_item:
        raise HTTPException(status_code=404, detail="BOM item not found")
    scenario = _get_scenario_or_404(payload.scenario_id) if payload.scenario_id else None

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


def _get_scenario_or_404(scenario_id: str):
    try:
        return _scenario_service.get_scenario(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
