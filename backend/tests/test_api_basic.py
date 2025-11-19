import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test_api.db"
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_pcf_methods():
    response = client.get("/pcf/methods")
    assert response.status_code == 200
    data = response.json()
    assert "methods" in data
    assert any(method["id"] == "PACT_V3" for method in data["methods"])


def test_product_bom_and_pcf_flow():
    product_payload = {
        "id": "prod-1",
        "name": "Laptop",
        "version": "1",
        "functional_unit": "1 device",
    }
    response = client.post("/products", json=product_payload)
    assert response.status_code == 200

    bom_payload = [
        {
            "id": "item-1",
            "product_id": "prod-1",
            "parent_bom_item_id": None,
            "description": "Aluminum housing",
            "quantity": 1,
            "unit": "ea",
            "mass_kg": 1.2,
            "material_family": "Aluminum",
            "material_code": "ALU-6000",
            "classification_unspsc": "000000",
            "supplier_id": None,
        }
    ]
    response = client.post("/bom/upload", json=bom_payload)
    assert response.status_code == 200

    review = client.get("/mapping/review/prod-1")
    assert review.status_code == 200
    assert len(review.json()) >= 1

    response = client.post("/pcf/run", json={"product_id": "prod-1", "pcf_method_id": "PACT_V3"})
    assert response.status_code == 200
    body = response.json()
    assert "pcf_total_kg_co2e" in body
    assert body["pcf_total_kg_co2e"] > 0

    history = client.get("/mapping/history/prod-1")
    assert history.status_code == 200
    assert len(history.json()) >= 1

    pci = client.get("/circularity/pci/prod-1")
    assert pci.status_code == 200
    pci_body = pci.json()
    assert "pci_product" in pci_body
