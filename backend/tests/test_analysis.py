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


def test_preprocess_scene_success_demo():
    payload = {
        "scene_id": "DEMO_S2A_20260115T053131_N0400_R005_T44QNF",
        "water_body_id": "gosikhurd-reservoir",
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
    
    response = client.post("/api/analysis/preprocess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data_source_mode"] == "demo"
    assert "quality" in data
    assert data["quality"]["valid_pixel_percentage"] > 0
    assert "bands" in data
    assert len(data["bands"]) > 0

def test_preprocess_scene_invalid_dates():
    payload = {
        "scene_id": "DEMO_S2A_20260115T053131",
        "water_body_id": "gosikhurd-reservoir",
        "start_date": "2026-03-31",
        "end_date": "2026-01-01", # reversed
        "aoi": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[79.62, 20.87], [79.64, 20.87], [79.64, 20.85], [79.62, 20.85], [79.62, 20.87]]]
            }
        }
    }
    response = client.post("/api/analysis/preprocess", json=payload)
    assert response.status_code == 400
    assert "Start date must be earlier" in response.json()["detail"]


def test_water_mask_success_demo():
    payload = {
        "scene_id": "DEMO_S2A_20260115T053131",
        "water_body_id": "gosikhurd-reservoir",
        "method": "combined",
        "threshold_method": "otsu",
        "aoi": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[79.62, 20.87], [79.64, 20.87], [79.64, 20.85], [79.62, 20.85], [79.62, 20.87]]]
            }
        }
    }
    
    response = client.post("/api/analysis/water-mask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data_source_mode"] == "demo"
    assert "water_area_km2" in data
    assert data["water_area_km2"] > 0
    assert "geometry" in data
    assert data["geometry"]["type"] == "FeatureCollection"

def test_water_mask_missing_aoi():
    payload = {
        "scene_id": "DEMO_S2A",
        "water_body_id": "test",
        "method": "combined",
        "aoi": None
    }
    response = client.post("/api/analysis/water-mask", json=payload)
    assert response.status_code == 400
    assert "Invalid AOI" in response.json()["detail"]

def test_otsu_calculation():
    from app.geospatial.water_detection.threshold import calculate_otsu_threshold
    
    # Bimodal distribution mock
    hist = []
    for i in range(10):
        hist.append([float(i), 10.0]) # background
    for i in range(90, 100):
        hist.append([float(i), 10.0]) # foreground
        
    threshold = calculate_otsu_threshold(hist)
    assert threshold is not None
    assert threshold == 9.0
    
    # Flat histogram
    flat_hist = [[1.0, 100.0]]
    assert calculate_otsu_threshold(flat_hist) is None

