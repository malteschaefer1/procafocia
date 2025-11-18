"""LCI mapping orchestration service with deterministic + fuzzy logic."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence

from rapidfuzz import fuzz

from ..core.config import get_settings
from ..data_providers.lci_provider_base import LCIProcessCandidate, LCIProvider
from ..models.bom import BOMItem
from ..models.scenario import Scenario
from .mapping_repository import MappingRepository


@dataclass
class MappingDecision:
    """Represents one mapping choice and its provenance."""

    item_id: str
    selected: LCIProcessCandidate | None
    alternatives: list[LCIProcessCandidate]
    reasoning: str
    rule_applied: str | None
    auto_selected: bool
    override_applied: bool
    confidence_score: float | None


class MappingService:
    """Coordinates provider queries, rule application, and persistence."""

    def __init__(self, providers: Sequence[LCIProvider], repository: MappingRepository, min_candidate: float, min_auto: float):
        self.providers = providers
        self.repository = repository
        self.min_candidate = min_candidate
        self.min_auto = min_auto

    @classmethod
    def from_settings(cls, providers: Sequence[LCIProvider], repository: MappingRepository) -> "MappingService":
        settings = get_settings()
        return cls(
            providers=providers,
            repository=repository,
            min_candidate=settings.mapping_min_similarity_for_candidate,
            min_auto=settings.mapping_min_similarity_for_auto_accept,
        )

    def map_bom(self, items: Iterable[BOMItem], scenario: Scenario | None = None) -> list[MappingDecision]:
        decisions: list[MappingDecision] = []
        with self.repository.session() as session:
            for item in items:
                override_model = self.repository.get_latest_override(session, item.id)
                if override_model:
                    decision = self._decision_from_model(override_model)
                    decisions.append(decision)
                    continue

                selected, alternatives, rule_code, reasoning, confidence = self._deterministic_mapping(session, item)
                if not selected:
                    selected, alternatives, rule_code, reasoning, confidence = self._fuzzy_mapping(item)

                decision = MappingDecision(
                    item_id=item.id,
                    selected=selected,
                    alternatives=alternatives,
                    reasoning=reasoning,
                    rule_applied=rule_code,
                    auto_selected=selected is not None,
                    override_applied=False,
                    confidence_score=confidence,
                )

                payload = {
                    "alternatives": [asdict(c) for c in alternatives],
                    "reasoning": reasoning,
                }
                self.repository.record_decision(
                    session,
                    product_id=item.product_id,
                    bom_item_id=item.id,
                    scenario_id=scenario.id if scenario else None,
                    selected_dataset_id=selected.dataset_id if selected else None,
                    selected_provider=selected.provider if selected else None,
                    confidence_score=confidence,
                    rule_applied=rule_code,
                    user_id=None,
                    comment=None,
                    decision_payload=payload,
                    auto_selected=selected is not None,
                )
                decisions.append(decision)
        return decisions

    def record_override(
        self,
        *,
        bom_item: BOMItem,
        dataset_id: str,
        provider: str,
        user_id: str | None,
        comment: str | None,
        scenario: Scenario | None = None,
    ) -> MappingDecision:
        candidate = LCIProcessCandidate(
            provider=provider,
            dataset_id=dataset_id,
            name="Manual override",
            description="User supplied override",
            confidence_score=1.0,
            mapping_rule_id="override",
            metadata={"user": user_id or "unknown"},
        )
        payload = {"overridden_by": user_id, "comment": comment}
        with self.repository.session() as session:
            model = self.repository.record_decision(
                session,
                product_id=bom_item.product_id,
                bom_item_id=bom_item.id,
                scenario_id=scenario.id if scenario else None,
                selected_dataset_id=dataset_id,
                selected_provider=provider,
                confidence_score=1.0,
                rule_applied="override",
                user_id=user_id,
                comment=comment,
                decision_payload=payload,
                auto_selected=False,
                is_override=True,
            )
        return MappingDecision(
            item_id=bom_item.id,
            selected=candidate,
            alternatives=[],
            reasoning=f"Manual override by {user_id or 'system'}",
            rule_applied="override",
            auto_selected=False,
            override_applied=True,
            confidence_score=1.0,
        )

    # --- Deterministic rules ---
    def _deterministic_mapping(self, session, item: BOMItem):
        if item.lci_dataset_id:
            candidate = LCIProcessCandidate(
                provider="manual",
                dataset_id=item.lci_dataset_id,
                name="BOM supplied dataset",
                description="BOM row referenced dataset id",
                confidence_score=0.99,
                mapping_rule_id="direct_lci_dataset",
                metadata={"source": "bom"},
            )
            return candidate, [], "direct_lci_dataset", "Dataset specified on BOM", candidate.confidence_score

        rule = self.repository.rule_by_material_code(session, item.material_code)
        if rule:
            candidate = self._candidate_from_rule(rule)
            return candidate, [], rule.rule_code, f"Matched material_code {item.material_code}", candidate.confidence_score

        rule = self.repository.rule_by_family_unspsc(session, item.material_family, item.classification_unspsc)
        if rule:
            candidate = self._candidate_from_rule(rule)
            return (
                candidate,
                [],
                rule.rule_code,
                f"Matched family {item.material_family} and UNSPSC {item.classification_unspsc}",
                candidate.confidence_score,
            )

        rule = self.repository.supplier_override(session, item.supplier_id, item.material_family, item.material_code)
        if rule:
            candidate = self._candidate_from_rule(rule)
            return (
                candidate,
                [],
                rule.rule_code,
                f"Supplier override for {item.supplier_id}",
                candidate.confidence_score,
            )

        return None, [], None, "No deterministic match", None

    def _candidate_from_rule(self, rule) -> LCIProcessCandidate:
        return LCIProcessCandidate(
            provider=rule.provider,
            dataset_id=rule.dataset_id,
            name=rule.name,
            description=rule.description or "Rule-derived dataset",
            confidence_score=0.95,
            mapping_rule_id=rule.rule_code,
            metadata={
                "rule_id": rule.id,
                "material_code": rule.material_code,
                "material_family": rule.material_family,
                "unspsc_prefix": rule.classification_unspsc_prefix,
            },
        )

    # --- Fuzzy matching ---
    def _fuzzy_mapping(self, item: BOMItem):
        target = " ".join(filter(None, [item.material_family or "", item.description or ""])).strip()
        if not target:
            target = item.description or item.id
        candidates: list[LCIProcessCandidate] = []
        for provider in self.providers:
            provider_candidates = provider.find_candidates(item)
            for cand in provider_candidates:
                reference = f"{cand.name} {cand.description}".strip()
                similarity = fuzz.token_set_ratio(target, reference) / 100
                cand.confidence_score = max(cand.confidence_score, similarity)
                candidates.append(cand)
        viable = [c for c in candidates if c.confidence_score >= self.min_candidate]
        viable.sort(key=lambda c: c.confidence_score, reverse=True)

        if viable and viable[0].confidence_score >= self.min_auto:
            selected = viable[0]
            reasoning = f"Auto-selected via fuzzy matching ({selected.confidence_score:.2f})"
            return selected, viable[1:], "fuzzy_auto", reasoning, selected.confidence_score

        reasoning = "Fuzzy matching produced candidates for review" if viable else "No candidates; manual mapping needed"
        return None, viable[:5], "fuzzy_review", reasoning, viable[0].confidence_score if viable else None

    def _decision_from_model(self, model) -> MappingDecision:
        selected = None
        if model.selected_dataset_id and model.selected_provider:
            selected = LCIProcessCandidate(
                provider=model.selected_provider,
                dataset_id=model.selected_dataset_id,
                name="Stored decision",
                description="Loaded from DB",
                confidence_score=model.confidence_score or 1.0,
                mapping_rule_id=model.rule_applied or "historical",
                metadata={"decision_id": model.id},
            )
        payload = json.loads(model.decision_payload) if model.decision_payload else {}
        alternatives = [LCIProcessCandidate(**entry) for entry in payload.get("alternatives", [])]
        reasoning = payload.get("reasoning", "Historical decision")
        return MappingDecision(
            item_id=model.bom_item_id,
            selected=selected,
            alternatives=alternatives,
            reasoning=reasoning,
            rule_applied=model.rule_applied,
            auto_selected=model.auto_selected,
            override_applied=model.is_override,
            confidence_score=model.confidence_score,
        )
