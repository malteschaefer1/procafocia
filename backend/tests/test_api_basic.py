from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
            "description": "Aluminum housing",
            "classification": "", 
            "material_code": "AL",
            "component_code": None,
            "mass_kg": 1.2,
            "quantity": 1,
        }
    ]
    response = client.post("/bom/upload", json=bom_payload)
    assert response.status_code == 200

    response = client.post("/pcf/run", json={"product_id": "prod-1"})
    assert response.status_code == 200
    body = response.json()
    assert "pcf_total_kg_co2e" in body
    assert body["pcf_total_kg_co2e"] > 0
