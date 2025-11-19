"""LCI mapping orchestration service with deterministic + fuzzy logic."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence

from rapidfuzz import fuzz

from ..core.config import get_settings
from ..data_providers.lci_provider_base import LCIProcessCandidate, LCIProvider
from ..data_providers.soda4lca_provider import Soda4LCAProvider
from ..engines.pcf_engine_base import LCIEntry, LCIModel
from ..integrations.soda4lca_client import Soda4LCAClient, get_soda_client, Soda4LCAError
from ..models.bom import BOMItem
from ..models.product import Product
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
    life_cycle_stage: str | None = None
    candidates: list[LCIProcessCandidate] | None = None


class MappingService:
    """Coordinates provider queries, rule application, and persistence."""

    def __init__(
        self,
        providers: Sequence[LCIProvider],
        repository: MappingRepository,
        min_candidate: float,
        min_auto: float,
        soda_client: Soda4LCAClient | None = None,
    ):
        self.providers = providers
        self.repository = repository
        self.min_candidate = min_candidate
        self.min_auto = min_auto
        self.soda_client = soda_client
        self.soda_provider = next((p for p in providers if isinstance(p, Soda4LCAProvider)), None)

    @classmethod
    def from_settings(cls, providers: Sequence[LCIProvider], repository: MappingRepository) -> "MappingService":
        settings = get_settings()
        return cls(
            providers=providers,
            repository=repository,
            min_candidate=settings.mapping_min_similarity_for_candidate,
            min_auto=settings.mapping_min_similarity_for_auto_accept,
            soda_client=get_soda_client(),
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

                life_cycle_stage = self._determine_stage(item, selected, rule_code)
                all_candidates: list[LCIProcessCandidate] = []
                if selected:
                    if not selected.life_cycle_stage:
                        selected.life_cycle_stage = life_cycle_stage
                    all_candidates.append(selected)
                for alt in alternatives:
                    if not alt.life_cycle_stage:
                        alt.life_cycle_stage = life_cycle_stage
                    all_candidates.append(alt)
                for cand in all_candidates:
                    self._ensure_brightway_reference(cand)
                decision = MappingDecision(
                    item_id=item.id,
                    selected=selected,
                    alternatives=alternatives,
                    reasoning=reasoning,
                    rule_applied=rule_code,
                    auto_selected=selected is not None,
                    override_applied=False,
                    confidence_score=confidence,
                    life_cycle_stage=life_cycle_stage,
                    candidates=all_candidates,
                )

                payload = {
                    "alternatives": [self._candidate_to_dict(c) for c in alternatives],
                    "candidates": [self._candidate_to_dict(c) for c in all_candidates],
                    "reasoning": reasoning,
                    "life_cycle_stage": life_cycle_stage,
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
        life_cycle_stage: str | None = None,
    ) -> MappingDecision:
        stage = self._normalize_stage(life_cycle_stage)
        candidate = LCIProcessCandidate(
            provider=provider,
            dataset_id=dataset_id,
            name="Manual override",
            description="User supplied override",
            confidence_score=1.0,
            mapping_rule_id="override",
            metadata={"user": user_id or "unknown"},
            life_cycle_stage=stage,
        )
        self._ensure_brightway_reference(candidate)
        payload = {
            "overridden_by": user_id,
            "comment": comment,
            "life_cycle_stage": stage,
            "candidates": [self._candidate_to_dict(candidate)],
        }
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
            life_cycle_stage=stage,
            candidates=[candidate],
        )

    # --- Deterministic rules ---
    def _deterministic_mapping(self, session, item: BOMItem):
        if item.lci_dataset_id:
            soda_candidate = self._lookup_soda_dataset(item.lci_dataset_id)
            if soda_candidate:
                return soda_candidate, [], "soda4lca_direct", "Dataset specified on BOM (soda4LCA)", soda_candidate.confidence_score
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
        payload = json.loads(model.decision_payload) if model.decision_payload else {}
        candidate_dicts = payload.get("candidates") or []
        candidates = [self._candidate_from_dict(entry) for entry in candidate_dicts]

        selected = None
        if model.selected_dataset_id and model.selected_provider:
            for cand in candidates:
                if cand.dataset_id == model.selected_dataset_id and cand.provider == model.selected_provider:
                    selected = cand
                    break
            if not selected:
                selected = LCIProcessCandidate(
                    provider=model.selected_provider,
                    dataset_id=model.selected_dataset_id,
                    name="Stored decision",
                    description="Loaded from DB",
                    confidence_score=model.confidence_score or 1.0,
                    mapping_rule_id=model.rule_applied or "historical",
                    metadata={"decision_id": model.id},
                )
                candidates.append(selected)

        alternatives = [cand for cand in candidates if cand is not selected]
        reasoning = payload.get("reasoning", "Historical decision")
        life_cycle_stage = payload.get("life_cycle_stage")
        return MappingDecision(
            item_id=model.bom_item_id,
            selected=selected,
            alternatives=alternatives,
            reasoning=reasoning,
            rule_applied=model.rule_applied,
            auto_selected=model.auto_selected,
            override_applied=model.is_override,
            confidence_score=model.confidence_score,
            life_cycle_stage=life_cycle_stage,
            candidates=candidates,
        )

    def load_latest_decisions(self, product_id: str) -> list[MappingDecision]:
        with self.repository.session() as session:
            models = self.repository.latest_decisions_for_product(session, product_id)
        return [self._decision_from_model(model) for model in models]

    def build_lci_model(
        self, product: Product, bom: list[BOMItem], scenario: Scenario | None = None
    ) -> tuple[LCIModel, list[MappingDecision]]:
        decisions = self.load_latest_decisions(product.id)
        if len(decisions) < len(bom):
            decisions = self.map_bom(bom, scenario)
        decision_map = {decision.item_id: decision for decision in decisions}
        entries: list[LCIEntry] = []
        for item in bom:
            decision = decision_map.get(item.id)
            if not decision or not decision.selected:
                raise ValueError(f"No confirmed mapping for BOM item {item.id}. Review mappings before running PCF.")
            stage = self._normalize_stage(decision.life_cycle_stage or decision.selected.life_cycle_stage)
            metadata = {}
            if decision.selected.metadata:
                metadata.update(decision.selected.metadata)
            if decision.rule_applied:
                metadata["rule_applied"] = decision.rule_applied
            metadata["auto_selected"] = decision.auto_selected
            entries.append(
                LCIEntry(
                    bom_item_id=item.id,
                    dataset_id=decision.selected.dataset_id,
                    provider=decision.selected.provider,
                    quantity=item.quantity,
                    unit=item.unit or "ea",
                    mass_kg=item.mass_kg,
                    life_cycle_stage=stage,
                    brightway_reference=decision.selected.brightway_reference,
                    metadata=metadata,
                )
            )
        lci_model = LCIModel(bom_items=bom, entries=entries)
        return lci_model, decisions

    def _determine_stage(
        self, item: BOMItem, candidate: LCIProcessCandidate | None, rule_code: str | None
    ) -> str:
        if candidate and candidate.life_cycle_stage:
            return self._normalize_stage(candidate.life_cycle_stage)
        if rule_code == "supplier_override" or (item.supplier_id and rule_code):
            return "own_operations"
        return self._normalize_stage(None)

    def _lookup_soda_dataset(self, dataset_id: str) -> LCIProcessCandidate | None:
        if not dataset_id or not self.soda_provider:
            return None
        uuid, version = self._parse_soda_identifier(dataset_id)
        if not uuid:
            return None
        return self.soda_provider.get_process_by_uuid(uuid, version)

    def _parse_soda_identifier(self, dataset_id: str) -> tuple[str | None, str | None]:
        value = dataset_id.strip()
        version = None
        if value.lower().startswith("soda4lca:"):
            value = value.split(":", 1)[1]
        if "?version=" in value:
            value, version = value.split("?version=", 1)
        elif "@" in value:
            value, version = value.split("@", 1)
        value = value.strip()
        if version:
            version = version.strip()
        if not value:
            return None, None
        return value, version

    def _normalize_stage(self, stage: str | None) -> str:
        allowed = {
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "purchased_energy",
            "use_phase",
            "end_of_life",
        }
        if not stage:
            return "raw_materials"
        key = stage.lower().replace("-", "_")
        if key not in allowed:
            return "raw_materials"
        return key

    def _ensure_brightway_reference(self, candidate: LCIProcessCandidate) -> None:
        if not candidate or candidate.brightway_reference or not self.soda_client:
            return
        try:
            candidate.brightway_reference = self.soda_client.build_brightway_reference(
                candidate.provider, candidate.dataset_id
            )
        except Soda4LCAError as exc:
            metadata = candidate.metadata or {}
            warnings = metadata.get("warnings", [])
            warnings.append(str(exc))
            metadata["warnings"] = warnings
            candidate.metadata = metadata

    def _candidate_to_dict(self, candidate: LCIProcessCandidate) -> dict:
        return {
            "provider": candidate.provider,
            "dataset_id": candidate.dataset_id,
            "name": candidate.name,
            "description": candidate.description,
            "confidence_score": candidate.confidence_score,
            "mapping_rule_id": candidate.mapping_rule_id,
            "metadata": candidate.metadata,
            "life_cycle_stage": candidate.life_cycle_stage,
            "brightway_reference": candidate.brightway_reference,
        }

    def _candidate_from_dict(self, data: dict) -> LCIProcessCandidate:
        return LCIProcessCandidate(
            provider=data.get("provider", ""),
            dataset_id=data.get("dataset_id", ""),
            name=data.get("name"),
            description=data.get("description"),
            confidence_score=data.get("confidence_score"),
            mapping_rule_id=data.get("mapping_rule_id") or "",
            metadata=data.get("metadata") or {},
            life_cycle_stage=data.get("life_cycle_stage"),
            brightway_reference=data.get("brightway_reference"),
        )
