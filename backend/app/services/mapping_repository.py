"""Persistence helpers for mapping rules and decisions."""
from __future__ import annotations

import json
from typing import Sequence

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from ..db.base import get_session
from ..db.models import MappingDecisionModel, MappingRuleModel


class MappingRepository:
    """Wraps SQLAlchemy persistence for mapping artifacts."""

    def __init__(self, session_factory=get_session):
        self._session_factory = session_factory

    def session(self) -> Session:
        return self._session_factory()

    # --- Rule lookups ---
    def _first_rule(self, session: Session, stmt: Select) -> MappingRuleModel | None:
        return session.scalars(stmt.order_by(MappingRuleModel.priority.asc())).first()

    def rule_by_material_code(self, session: Session, material_code: str | None) -> MappingRuleModel | None:
        if not material_code:
            return None
        stmt = select(MappingRuleModel).where(MappingRuleModel.material_code == material_code)
        return self._first_rule(session, stmt)

    def rule_by_family_unspsc(
        self, session: Session, material_family: str | None, classification_unspsc: str | None
    ) -> MappingRuleModel | None:
        if not material_family or not classification_unspsc:
            return None
        stmt = select(MappingRuleModel).where(
            (MappingRuleModel.material_family == material_family)
            & (MappingRuleModel.classification_unspsc_prefix.is_not(None))
        )
        rules = session.scalars(stmt.order_by(MappingRuleModel.priority.asc())).all()
        for rule in rules:
            prefix = rule.classification_unspsc_prefix or ""
            if classification_unspsc.startswith(prefix):
                return rule
        return None

    def supplier_override(
        self,
        session: Session,
        supplier_id: str | None,
        material_family: str | None,
        material_code: str | None,
    ) -> MappingRuleModel | None:
        if not supplier_id:
            return None
        stmt = select(MappingRuleModel).where(MappingRuleModel.supplier_id == supplier_id)
        rules = session.scalars(stmt.order_by(MappingRuleModel.priority.asc())).all()
        for rule in rules:
            if rule.material_code and rule.material_code != material_code:
                continue
            if rule.material_family and rule.material_family != material_family:
                continue
            return rule
        return None

    def list_rules(self, session: Session) -> Sequence[MappingRuleModel]:
        stmt = select(MappingRuleModel).order_by(MappingRuleModel.priority.asc())
        return session.scalars(stmt).all()

    # --- Decisions ---
    def get_latest_decision(self, session: Session, bom_item_id: str) -> MappingDecisionModel | None:
        stmt = (
            select(MappingDecisionModel)
            .where(MappingDecisionModel.bom_item_id == bom_item_id)
            .order_by(desc(MappingDecisionModel.created_at))
        )
        return session.scalars(stmt).first()

    def get_latest_override(self, session: Session, bom_item_id: str) -> MappingDecisionModel | None:
        stmt = (
            select(MappingDecisionModel)
            .where((MappingDecisionModel.bom_item_id == bom_item_id) & (MappingDecisionModel.is_override.is_(True)))
            .order_by(desc(MappingDecisionModel.created_at))
        )
        return session.scalars(stmt).first()

    def record_decision(
        self,
        session: Session,
        *,
        product_id: str,
        bom_item_id: str,
        scenario_id: str | None,
        selected_dataset_id: str | None,
        selected_provider: str | None,
        confidence_score: float | None,
        rule_applied: str | None,
        user_id: str | None,
        comment: str | None,
        decision_payload: dict,
        auto_selected: bool,
        is_override: bool = False,
    ) -> MappingDecisionModel:
        model = MappingDecisionModel(
            product_id=product_id,
            bom_item_id=bom_item_id,
            scenario_id=scenario_id,
            selected_dataset_id=selected_dataset_id,
            selected_provider=selected_provider,
            confidence_score=confidence_score,
            rule_applied=rule_applied,
            user_id=user_id,
            comment=comment,
            decision_payload=json.dumps(decision_payload),
            auto_selected=auto_selected,
            is_override=is_override,
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def list_history_for_product(self, session: Session, product_id: str) -> list[MappingDecisionModel]:
        stmt = (
            select(MappingDecisionModel)
            .where(MappingDecisionModel.product_id == product_id)
            .order_by(desc(MappingDecisionModel.created_at))
        )
        return list(session.scalars(stmt).all())
