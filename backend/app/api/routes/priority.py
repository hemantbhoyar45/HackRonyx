from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

MOCK_PRIORITY_QUEUE = [
    {
        "id": "p_001",
        "rank": 1,
        "water_body": "Gosikhurd Reservoir",
        "zone": "North Basin",
        "date": "2026-09-22",
        "priority_score": 88,
        "severity": "High",
        "confidence": 92,
        "primary_indicator": "Turbidity",
        "investigation_status": "Pending",
    },
    {
        "id": "p_002",
        "rank": 2,
        "water_body": "Godavari River \u2013 Selected Segment",
        "zone": "Industrial Outflow A",
        "date": "2026-09-21",
        "priority_score": 75,
        "severity": "Medium",
        "confidence": 85,
        "primary_indicator": "Chlorophyll",
        "investigation_status": "In Progress",
    }
]

@router.get("/")
def get_priority_queue() -> List[Dict[str, Any]]:
    return MOCK_PRIORITY_QUEUE
