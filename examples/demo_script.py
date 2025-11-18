"""Example script demonstrating BOM ingestion + stub calculations."""
from __future__ import annotations

from pathlib import Path
import argparse

from backend.app.engines.circularity_engine_pci_bracquene2020 import Bracquene2020CircularityEngine
from backend.app.engines.pcf_engine_brightway import BrightwayPCFEngine
from backend.app.models.product import Product
from backend.app.services.circularity_service import CircularityService
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.mapping_repository import MappingRepository
from backend.app.services.mapping_service import MappingService
from backend.app.services.pcf_service import PCFService
from backend.app.services.scenario_service import ScenarioService
from backend.app.data_providers.probas_provider import ProBasProvider
from backend.app.data_providers.boavizta_provider import BoaviztaProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demo mapping + calculation flow")
    parser.add_argument(
        "--bom",
        default=str(Path(__file__).with_name("bom_office_chair.csv")),
        help="Path to canonical BOM CSV",
    )
    args = parser.parse_args()

    ingestion = IngestionService()
    bom_path = Path(args.bom)
    bom_items = ingestion.load_bom_from_csv(bom_path)

    scenario_service = ScenarioService()
    scenario = scenario_service.get_scenario("default")
    method = scenario_service.get_method_profile(scenario.method_profile_id)

    mapping_service = MappingService.from_settings([ProBasProvider(), BoaviztaProvider()], MappingRepository())
    mapping_log = mapping_service.map_bom(bom_items, scenario)

    product_id = bom_items[0].product_id if bom_items else "demo-product"
    product = Product(id=product_id, name="Demo Product", version="1", functional_unit="1 unit")

    pcf_service = PCFService(BrightwayPCFEngine())
    pcf_results = pcf_service.run(bom_items, scenario, method)

    circularity_service = CircularityService(Bracquene2020CircularityEngine())
    circularity_results = circularity_service.run(product, bom_items, scenario)

    print("Mapping decisions:")
    for entry in mapping_log:
        print(entry)

    print("\nPCF total (kg CO2e):", pcf_results.pcf_total_kg_co2e)
    pci_payload = circularity_results.circularity_indicators.get("pci_result", {})
    print("Circularity PCI score:", pci_payload.get("pci_product"))


if __name__ == "__main__":
    main()
