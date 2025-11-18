"""Audit bundle export utilities."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from typing import Iterable

from ..models.bom import BOMItem
from ..models.method_profile import MethodProfile
from ..models.product import Product
from ..models.results import ResultSet
from ..models.scenario import Scenario
from .mapping_service import MappingDecision


def build_audit_bundle(
    product: Product,
    bom: Iterable[BOMItem],
    scenario: Scenario,
    method_profile: MethodProfile,
    mapping_decisions: Iterable[MappingDecision],
    result_sets: Iterable[ResultSet],
    as_zip: bool = False,
) -> bytes | str:
    """Create a JSON or zipped JSON audit artifact."""

    bundle = {
        "product": product.__dict__,
        "scenario": scenario.__dict__,
        "method_profile": method_profile.__dict__,
        "bom": [item.__dict__ for item in bom],
        "mapping_log": [
            {
                "item_id": d.item_id,
                "selected": d.selected.__dict__ if d.selected else None,
                "alternatives": [alt.__dict__ for alt in d.alternatives],
                "reasoning": d.reasoning,
            }
            for d in mapping_decisions
        ],
        "results": [r.__dict__ for r in result_sets],
    }

    if not as_zip:
        return json.dumps(bundle, indent=2)

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("audit_bundle.json", json.dumps(bundle, indent=2))
    buffer.seek(0)
    return buffer.read()
