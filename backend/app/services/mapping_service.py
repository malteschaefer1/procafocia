"""LCI mapping orchestration service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ..models.bom import BOMItem
from ..models.scenario import Scenario
from ..data_providers.lci_provider_base import LCIProcessCandidate, LCIProvider


@dataclass
class MappingDecision:
    """Represents one mapping choice and its provenance."""

    item_id: str
    selected: LCIProcessCandidate | None
    alternatives: list[LCIProcessCandidate]
    reasoning: str


class MappingService:
    """Coordinates provider queries and mapping logs."""

    def __init__(self, providers: Sequence[LCIProvider]):
        self.providers = providers

    def map_bom(self, items: Iterable[BOMItem], scenario: Scenario | None = None) -> list[MappingDecision]:
        decisions: list[MappingDecision] = []
        for item in items:
            candidates: list[LCIProcessCandidate] = []
            for provider in self.providers:
                provider_candidates = provider.find_candidates(item)
                candidates.extend(provider_candidates)
            selected = self._select_candidate(candidates)
            reasoning = self._build_reasoning(selected, scenario)
            decisions.append(
                MappingDecision(
                    item_id=item.id,
                    selected=selected,
                    alternatives=[c for c in candidates if c is not selected],
                    reasoning=reasoning,
                )
            )
        return decisions

    def _select_candidate(self, candidates: list[LCIProcessCandidate]) -> LCIProcessCandidate | None:
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.confidence_score)

    def _build_reasoning(self, candidate: LCIProcessCandidate | None, scenario: Scenario | None) -> str:
        if not candidate:
            return "No candidate found - manual mapping required."
        base = f"Selected {candidate.provider}:{candidate.dataset_id} via rule {candidate.mapping_rule_id}"
        if scenario:
            base += f" for scenario {scenario.name}"
        return base
