from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# Mock data for initial UI
MOCK_WATER_BODIES = [
    {"id": "wb_001", "name": "Gosikhurd Reservoir", "type": "reservoir"},
    {"id": "wb_002", "name": "Godavari River \u2013 Selected Segment", "type": "river"},
    {"id": "wb_003", "name": "Wainganga River \u2013 Selected Segment", "type": "river"},
    {"id": "wb_004", "name": "Jaikwadi Reservoir", "type": "reservoir"},
]

@router.get("/water-bodies")
def get_water_bodies() -> List[Dict[str, Any]]:
    return MOCK_WATER_BODIES

@router.get("/status")
def get_dashboard_status() -> Dict[str, Any]:
    return {
        "overall_status": "Potential Anomaly",
        "priority_score": 75,
        "confidence": 82,
        "affected_area_km2": 12.4,
        "indicator_summary": {
            "turbidity": "High",
            "chlorophyll": "Elevated",
            "suspended_sediment": "Normal"
        }
    }
