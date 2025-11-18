import math

from backend.app.engines.circularity_engine_pci_bracquene2020 import Bracquene2020CircularityEngine
from backend.app.models.bom import BOMItem
from backend.app.models.pci import MaterialCircularityParameters
from backend.app.models.product import Product
from backend.app.models.scenario import Scenario
from backend.app.services.circularity_service import CircularityService


def _make_bom_item(material: str, mass: float, reused: float = 0.0, recycled: float = 0.0) -> BOMItem:
    return BOMItem(
        id=f"item-{material}",
        product_id="prod-test",
        parent_bom_item_id=None,
        description=f"{material} part",
        quantity=1.0,
        unit="ea",
        mass_kg=mass,
        material_family=material,
        material_code=material,
        classification_unspsc="000000",
        supplier_id=None,
        component_code=None,
        recycled_content_share=recycled,
        reused_share=reused,
    )


def _base_param(material_key: str) -> MaterialCircularityParameters:
    return MaterialCircularityParameters(
        material_key=material_key,
        efficiency_feedstock_production=0.85,
        efficiency_component_production=0.9,
        recovered_fraction_feedstock_losses=0.6,
        recovered_fraction_component_losses=0.6,
        efficiency_material_separation_eol=0.8,
        efficiency_recycled_feedstock_production=0.85,
    )


def _make_scenario(collection_reuse: float, collection_recycling: float, utility_factor: float, params: dict[str, MaterialCircularityParameters]) -> Scenario:
    return Scenario(
        id="scenario-test",
        name="Test",
        goal_scope="",
        system_boundary="",
        geography="",
        method_profile_id="iso-basic",
        energy_mix_profile="",
        end_of_life_model="",
        collection_fraction_for_reuse=collection_reuse,
        collection_fraction_for_recycling=collection_recycling,
        utility_factor=utility_factor,
        material_parameters=params,
    )


def test_linear_flow_results_in_low_pci():
    service = CircularityService(Bracquene2020CircularityEngine())
    params = {"Steel": _base_param("Steel")}
    scenario = _make_scenario(0.0, 0.0, 1.0, params)
    product = Product(id="prod-test", name="Test", version="1", functional_unit="1")
    bom = [_make_bom_item("Steel", 5.0)]

    result = service.calculate_pci(product, bom, scenario)
    assert result.pci_product <= 0.05


def test_high_circularity_increases_pci():
    service = CircularityService(Bracquene2020CircularityEngine())
    params = {"Aluminum": _base_param("Aluminum")}
    scenario = _make_scenario(0.5, 0.9, 1.2, params)
    product = Product(id="prod-test", name="Test", version="1", functional_unit="1")
    bom = [_make_bom_item("Aluminum", 3.0, reused=0.4, recycled=0.5)]

    result = service.calculate_pci(product, bom, scenario)
    assert result.pci_product > 0.4


def test_mass_weighted_pci_matches_material_flows():
    service = CircularityService(Bracquene2020CircularityEngine())
    params = {
        "Steel": _base_param("Steel"),
        "Polymer": _base_param("Polymer"),
    }
    scenario = _make_scenario(0.2, 0.6, 1.0, params)
    product = Product(id="prod-test", name="Test", version="1", functional_unit="1")
    bom = [_make_bom_item("Steel", 2.0, recycled=0.3), _make_bom_item("Polymer", 1.0, recycled=0.1)]

    result = service.calculate_pci(product, bom, scenario)
    weighted = sum(flow.mass * flow.PCI_material for flow in result.per_material_flows) / result.mass_total
    assert math.isclose(result.pci_product, weighted, rel_tol=1e-6)
