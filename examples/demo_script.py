"""Example script demonstrating BOM ingestion + stub calculations."""
from __future__ import annotations

from pathlib import Path

from backend.app.engines.circularity_engine_pci_bracquene2020 import Bracquene2020CircularityEngine
from backend.app.engines.pcf_engine_brightway import BrightwayPCFEngine
from backend.app.models.product import Product
from backend.app.services.circularity_service import CircularityService
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.mapping_service import MappingService
from backend.app.services.pcf_service import PCFService
from backend.app.services.scenario_service import ScenarioService
from backend.app.data_providers.probas_provider import ProBasProvider
from backend.app.data_providers.boavizta_provider import BoaviztaProvider


def main() -> None:
    ingestion = IngestionService()
    bom_path = Path(__file__).with_name("example_bom.csv")
    bom_items = ingestion.load_bom_from_csv(bom_path)

    scenario_service = ScenarioService()
    scenario = scenario_service.get_scenario("default")
    method = scenario_service.get_method_profile(scenario.method_profile_id)

    mapping_service = MappingService([ProBasProvider(), BoaviztaProvider()])
    mapping_log = mapping_service.map_bom(bom_items, scenario)

    product = Product(id="prod-1", name="Demo Product", version="1", functional_unit="1 unit")

    pcf_service = PCFService(BrightwayPCFEngine())
    pcf_results = pcf_service.run(bom_items, scenario, method)

    circularity_service = CircularityService(Bracquene2020CircularityEngine())
    circularity_results = circularity_service.run(product, bom_items, scenario)

    print("Mapping decisions:")
    for entry in mapping_log:
        print(entry)

    print("\nPCF total (kg CO2e):", pcf_results.pcf_total_kg_co2e)
    print("Circularity PCI score:", circularity_results.circularity_indicators.get("pci"))


if __name__ == "__main__":
    main()
