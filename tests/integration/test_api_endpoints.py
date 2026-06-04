import pytest
from fastapi.testclient import TestClient
from src.ingestion_api.main import app
from src.common.db.connection import get_session
from src.ingestion_api.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_get_session(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    yield
    app.dependency_overrides.clear()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_create_and_get_supplier():
    headers = {"X-API-Key": settings.API_KEY}
    
    create_data = {
        "supplier_code": "NEW_SUPP",
        "name": "New Test Supplier",
        "location": "Somewhere",
        "tier": "tier_2",
        "contact_info": {"email": "test@test.com"}
    }
    response = client.post(f"{settings.API_V1_STR}/suppliers/", json=create_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["supplier_code"] == "NEW_SUPP"
    
    response = client.get(f"{settings.API_V1_STR}/suppliers/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert any(s["supplier_code"] == "NEW_SUPP" for s in data)

def test_telemetry_batch():
    headers = {"X-API-Key": settings.API_KEY}
    
    batch_data = {
        "records": [
            {
                "supplier_code": "NEW_SUPP",
                "equipment_code": "EQ1",
                "product_line_code": "PL1",
                "timestamp": "2023-10-10T10:00:00Z",
                "cycle_time_seconds": 10.5,
                "units_produced": 100,
                "units_passed": 95,
                "temperature_c": 50.0,
                "pressure_psi": 100.0,
                "vibration_mm_s": 2.5,
                "power_consumption_kw": 10.0,
                "process_params": {}
            }
        ]
    }
    
    response = client.post(f"{settings.API_V1_STR}/telemetry/batch", json=batch_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "accepted" in data

def test_get_latest_telemetry():
    headers = {"X-API-Key": settings.API_KEY}
    
    response = client.get(f"{settings.API_V1_STR}/telemetry/latest/NEW_SUPP", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
