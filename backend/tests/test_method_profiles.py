import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test_methods.db"
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from backend.app.db.init_db import init_db  # noqa: E402
from backend.app.models.method_profile import PCF_METHOD_PROFILES, PCFMethodID  # noqa: E402
from backend.app.services.scenario_service import ScenarioService  # noqa: E402

init_db()


def test_method_registry_contains_pact():
    assert PCFMethodID.PACT_V3 in PCF_METHOD_PROFILES
    profile = PCF_METHOD_PROFILES[PCFMethodID.PACT_V3]
    assert profile.requires_dqr_scoring is True
    assert profile.system_boundary == "cradle_to_gate"


def test_default_scenario_uses_pact_method():
    service = ScenarioService()
    scenario = service.get_scenario("default")
    assert scenario.pcf_method_id == PCFMethodID.PACT_V3
