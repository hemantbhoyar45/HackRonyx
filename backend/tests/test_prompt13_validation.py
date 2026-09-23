import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_demo_endpoint():
    """Test the demo data generation endpoint."""
    response = client.get("/api/validation/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["data_source_mode"] == "DEMO DATA"
    assert "validation_record" in data
    assert "lab_results" in data
    assert "comparison_result" in data
    
    comp = data["comparison_result"]
    assert comp["validation_status"] == "SUPPORTED"
    assert comp["satellite_indicator"] == "ndti"
    assert comp["related_lab_parameter"] == "Turbidity"
    assert comp["temporal_difference_days"] == 1
    assert comp["spatial_relation"] == "INSIDE_ALERT_ZONE"


def test_field_sample_lifecycle():
    """Test creating a field sample and adding a lab result."""
    # 1. Create Sample
    sample_payload = {
        "water_body_id": "test-body",
        "zone_id": "zone-c",
        "sample_date": "2026-09-20",
        "latitude": 21.5,
        "longitude": 79.5,
        "sample_type": "SURFACE_WATER"
    }
    resp = client.post("/api/validation/samples", json=sample_payload)
    assert resp.status_code == 200
    sample = resp.json()
    assert sample["water_body_id"] == "test-body"
    assert sample["validation_status"] == "FIELD_COLLECTED"
    
    sample_id = sample["sample_id"]
    val_id = sample["validation_id"]
    
    # 2. Get Sample
    resp = client.get(f"/api/validation/samples/{sample_id}")
    assert resp.status_code == 200
    assert resp.json()["sample_id"] == sample_id
    
    # 3. Add Lab Result
    lab_payload = {
        "validation_id": val_id,
        "parameter_name": "TSS",
        "value": 45.0,
        "unit": "mg/L"
    }
    resp = client.post(f"/api/validation/samples/{sample_id}/lab-results", json=lab_payload)
    assert resp.status_code == 200
    lab_res = resp.json()
    assert lab_res["parameter_name"] == "TSS"
    
    # 4. Check status advanced to LAB_AVAILABLE
    resp = client.get(f"/api/validation/{val_id}")
    assert resp.status_code == 200
    assert resp.json()["validation_status"] == "LAB_AVAILABLE"
    
    # 5. Run Comparison (with no anomaly context, should be inconclusive)
    resp = client.post(f"/api/validation/{val_id}/compare", json={})
    assert resp.status_code == 200
    comp = resp.json()
    assert comp["validation_status"] == "INCONCLUSIVE"
    assert "No significant satellite anomaly" in comp["explanation"]


def test_validation_comparison_supported():
    """Test the comparison engine with compatible evidence."""
    sample_payload = {
        "water_body_id": "test-body-2",
        "zone_id": "zone-a",
        "sample_date": "2026-10-01",
        "latitude": 20.0,
        "longitude": 80.0,
        "sample_type": "LAKE_WATER"
    }
    resp = client.post("/api/validation/samples", json=sample_payload)
    sample = resp.json()
    val_id = sample["validation_id"]
    
    # Lab result matching NDTI
    client.post(f"/api/validation/samples/{sample['sample_id']}/lab-results", json={
        "validation_id": val_id,
        "parameter_name": "Turbidity",
        "value": 25.0,
        "unit": "NTU",
        "reference_max": 15.0 # This makes it elevated
    })
    
    # Context showing elevated NDTI on the same day, same location
    anomaly_context = {
        "indicator": "ndti",
        "current_value": 0.2,
        "baseline_median": 0.1,
        "deviation_relative": 0.1, # Positive deviation = elevated
        "analysis_date": "2026-10-01",
        "zone_lat": 20.0,
        "zone_lon": 80.0
    }
    
    resp = client.post(f"/api/validation/{val_id}/compare", json=anomaly_context)
    assert resp.status_code == 200
    comp = resp.json()
    
    assert comp["validation_status"] == "SUPPORTED"
    assert comp["temporal_relation"] == "SAME_DAY"
    assert comp["spatial_relation"] == "INSIDE_ALERT_ZONE"


def test_validation_comparison_not_supported():
    """Test the comparison engine with conflicting evidence."""
    sample_payload = {
        "water_body_id": "test-body-3",
        "sample_date": "2026-10-01",
        "latitude": 20.0,
        "longitude": 80.0,
        "sample_type": "LAKE_WATER"
    }
    resp = client.post("/api/validation/samples", json=sample_payload)
    val_id = resp.json()["validation_id"]
    
    # Lab result NOT elevated (value < ref_max and value < ref_min)
    client.post(f"/api/validation/samples/{resp.json()['sample_id']}/lab-results", json={
        "validation_id": val_id,
        "parameter_name": "Chlorophyll-a",
        "value": 2.0,
        "unit": "ug/L",
        "reference_min": 5.0,
        "reference_max": 15.0
    })
    
    # Context showing elevated NDCI
    anomaly_context = {
        "indicator": "ndci",
        "deviation_relative": 0.3, # elevated
        "analysis_date": "2026-10-01",
        "zone_lat": 20.0,
        "zone_lon": 80.0
    }
    
    resp = client.post(f"/api/validation/{val_id}/compare", json=anomaly_context)
    assert resp.status_code == 200
    comp = resp.json()
    
    assert comp["validation_status"] == "NOT_SUPPORTED"
    assert "does not show compatible directional evidence" in comp["explanation"]


def test_validation_status_update_and_history():
    """Test manual status updates and history tracking."""
    sample_payload = {
        "water_body_id": "test-body-4",
        "sample_date": "2026-10-01",
        "latitude": 20.0,
        "longitude": 80.0,
        "sample_type": "LAKE_WATER"
    }
    resp = client.post("/api/validation/samples", json=sample_payload)
    val_id = resp.json()["validation_id"]
    
    # Manual update
    resp = client.patch(f"/api/validation/{val_id}/status", json={
        "status": "REVIEW_REQUIRED",
        "reason": "Need expert review"
    })
    assert resp.status_code == 200
    assert resp.json()["validation_status"] == "REVIEW_REQUIRED"
    
    # Check history
    resp = client.get(f"/api/validation/{val_id}/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) > 0
    
    # Most recent update should be our manual one
    latest = sorted(history, key=lambda x: x["changed_at"])[-1]
    assert latest["new_status"] == "REVIEW_REQUIRED"
    assert latest["reason"] == "Need expert review"
