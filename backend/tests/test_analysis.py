from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_prepare_analysis_success():
    payload = {
        "water_body_id": "gosikhurd-reservoir",
        "water_body_name": "Gosikhurd Reservoir",
        "start_date": "2026-01-01",
        "end_date": "2026-03-31",
        "aoi": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[79.62, 20.87], [79.64, 20.87], [79.64, 20.85], [79.62, 20.85], [79.62, 20.87]]]
            }
        }
    }
    
    response = client.post("/api/analysis/prepare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["water_body_id"] == "gosikhurd-reservoir"

def test_prepare_analysis_invalid_dates():
    payload = {
        "water_body_id": "gosikhurd-reservoir",
        "water_body_name": "Gosikhurd Reservoir",
        "start_date": "2026-03-31",
        "end_date": "2026-01-01", # End date before start date
        "aoi": {}
    }
    
    response = client.post("/api/analysis/prepare", json=payload)
    assert response.status_code == 400
    assert "Start date must be earlier" in response.json()["detail"]
