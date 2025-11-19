"""Database initialization helpers."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from ..data.default_scenarios import default_scenarios
from .base import Base, engine, get_session
from .models import MappingRuleModel, ScenarioModel


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def init_db() -> None:
    """Create tables and seed canonical data if needed."""

    Base.metadata.create_all(bind=engine)
    ensure_schema_upgrades()
    seed_mapping_rules()
    seed_scenarios()


def seed_mapping_rules() -> None:
    rules_path = DATA_DIR / "mapping_rules_seed.json"
    if not rules_path.exists():
        return
    payload = json.loads(rules_path.read_text())
    with get_session() as session:
        for entry in payload:
            stmt = select(MappingRuleModel).where(
                (MappingRuleModel.rule_code == entry["rule_code"])
                & (MappingRuleModel.dataset_id == entry["dataset_id"])
                & (MappingRuleModel.material_code == entry.get("material_code"))
                & (MappingRuleModel.material_family == entry.get("material_family"))
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


def seed_scenarios() -> None:
    payload = default_scenarios()
    with get_session() as session:
        for entry in payload:
            existing = session.get(ScenarioModel, entry["id"])
            if existing:
                continue
            scenario = ScenarioModel(
                id=entry["id"],
                name=entry["name"],
                goal_scope=entry["goal_scope"],
                system_boundary=entry["system_boundary"],
                geography=entry["geography"],
                method_profile_id=entry["method_profile_id"],
                energy_mix_profile=entry["energy_mix_profile"],
                end_of_life_model=entry["end_of_life_model"],
                collection_fraction_for_reuse=entry.get("collection_fraction_for_reuse", 0.0),
                collection_fraction_for_recycling=entry.get("collection_fraction_for_recycling", 0.0),
                utility_factor=entry.get("utility_factor"),
                design_lifetime_functional_units=entry.get("design_lifetime_functional_units"),
                actual_used_functional_units=entry.get("actual_used_functional_units"),
                material_parameters=json.dumps(entry.get("material_parameters", {})),
            )
            session.add(scenario)
        session.commit()


def ensure_schema_upgrades() -> None:
    """Apply lightweight schema tweaks for SQLite deployments."""

    with engine.connect() as conn:
        # Scenario table adjustments
        scenario_cols = {row["name"] for row in conn.exec_driver_sql("PRAGMA table_info(scenarios)").mappings()}
        if "pcf_method_id" not in scenario_cols:
            conn.exec_driver_sql("ALTER TABLE scenarios ADD COLUMN pcf_method_id TEXT DEFAULT 'PACT_V3'")

        # Product table adjustments
        product_cols = {row["name"] for row in conn.exec_driver_sql("PRAGMA table_info(products)").mappings()}
        if "lifetime_years" not in product_cols:
            conn.exec_driver_sql("ALTER TABLE products ADD COLUMN lifetime_years FLOAT")
        if "use_profile" not in product_cols:
            conn.exec_driver_sql("ALTER TABLE products ADD COLUMN use_profile TEXT")
