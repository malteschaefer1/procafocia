import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test_mapping.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from backend.app.db.init_db import init_db  # noqa: E402
from backend.app.models.bom import BOMItem  # noqa: E402
from backend.app.models.scenario import Scenario  # noqa: E402
from backend.app.services.mapping_repository import MappingRepository  # noqa: E402
from backend.app.services.mapping_service import MappingService  # noqa: E402


def _make_item(material_code: str) -> BOMItem:
    return BOMItem(
        id="i1",
        product_id="prod-chair",
        parent_bom_item_id=None,
        description="Aluminum part",
        quantity=1,
        unit="ea",
        mass_kg=2.0,
        material_family="Aluminum",
        material_code=material_code,
        classification_unspsc="56112105",
        supplier_id=None,
    )


def test_mapping_service_uses_material_code_rule():
    init_db()
    repository = MappingRepository()
    service = MappingService(providers=[], repository=repository, min_candidate=0.6, min_auto=0.85)

    scenario = Scenario(
        id="default",
        name="Default",
        goal_scope="",
        system_boundary="",
        geography="",
        method_profile_id="iso-basic",
        energy_mix_profile="",
        end_of_life_model="",
    )

    decisions = service.map_bom([_make_item("ALU-6000")], scenario)
    assert decisions[0].selected is not None
    assert decisions[0].selected.dataset_id == "prob:aluminium-extrusion"
