from backend.app.engines.pcf_engine_base import PCFResult
from backend.app.models.bom import BOMItem
from backend.app.models.method_profile import PCF_METHOD_PROFILES, PCFMethodID
from backend.app.models.product import Product
from backend.app.models.scenario import Scenario
from backend.app.services.pcf_service import PCFService


class _FakeEngine:
    def __init__(self):
        self.last_method_id = None

    def calculate_pcf(self, product, bom_items, scenario, method_profile, lci_model=None):
        self.last_method_id = method_profile.id
        total = sum(item.mass_kg for item in bom_items)
        return PCFResult(
            total_kg_co2e=total,
            breakdown_by_item={item.id: item.mass_kg for item in bom_items},
            breakdown_by_stage={"total": total},
            provenance={},
        )


def _make_scenario(method_id: PCFMethodID) -> Scenario:
    return Scenario(
        id="scen",
        name="Test",
        goal_scope="",
        system_boundary="",
        geography="",
        method_profile_id=method_id.value,
        pcf_method_id=method_id,
        energy_mix_profile="",
        end_of_life_model="",
    )


def _make_bom(product_id: str) -> list[BOMItem]:
    return [
        BOMItem(
            id="item",
            product_id=product_id,
            parent_bom_item_id=None,
            description="Test",
            quantity=1.0,
            unit="ea",
            mass_kg=1.0,
            material_family="Steel",
            material_code="STL",
            classification_unspsc="",
            supplier_id=None,
        )
    ]


def test_pcf_service_passes_method_profile():
    engine = _FakeEngine()
    service = PCFService(engine)
    product = Product(id="prod", name="Prod", version="1", functional_unit="1")
    bom = _make_bom(product.id)
    scenario = _make_scenario(PCFMethodID.PACT_V3)
    method_profile = PCF_METHOD_PROFILES[PCFMethodID.PACT_V3]

    result = service.run(product, bom, scenario, method_profile)

    assert engine.last_method_id == PCFMethodID.PACT_V3
    assert result.method_profile_id == PCFMethodID.PACT_V3.value


def test_pcf_service_handles_other_methods():
    engine = _FakeEngine()
    service = PCFService(engine)
    product = Product(id="prod", name="Prod", version="1", functional_unit="1")
    bom = _make_bom(product.id)
    scenario = _make_scenario(PCFMethodID.ISO14067_GENERIC)
    method_profile = PCF_METHOD_PROFILES[PCFMethodID.ISO14067_GENERIC]

    service.run(product, bom, scenario, method_profile)

    assert engine.last_method_id == PCFMethodID.ISO14067_GENERIC
