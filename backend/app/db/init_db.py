"""Database initialization helpers."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from .base import Base, engine, get_session
from .models import MappingRuleModel


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def init_db() -> None:
    """Create tables and seed canonical data if needed."""

    Base.metadata.create_all(bind=engine)
    seed_mapping_rules()


def seed_mapping_rules() -> None:
    rules_path = DATA_DIR / "mapping_rules_seed.json"
    if not rules_path.exists():
        return
    payload = json.loads(rules_path.read_text())
    with get_session() as session:
        for entry in payload:
            stmt = select(MappingRuleModel).where(
                (MappingRuleModel.rule_code == entry["rule_code"]) &
                (MappingRuleModel.dataset_id == entry["dataset_id"]) &
                (MappingRuleModel.material_code == entry.get("material_code")) &
                (MappingRuleModel.material_family == entry.get("material_family"))
            )
            exists = session.scalars(stmt).first()
            if exists:
                continue
            rule = MappingRuleModel(
                name=entry["name"],
                rule_code=entry["rule_code"],
                priority=entry.get("priority", 0),
                material_code=entry.get("material_code"),
                material_family=entry.get("material_family"),
                classification_unspsc_prefix=entry.get("classification_unspsc_prefix"),
                supplier_id=entry.get("supplier_id"),
                dataset_id=entry["dataset_id"],
                provider=entry["provider"],
                description=entry.get("description"),
            )
            session.add(rule)
        session.commit()
