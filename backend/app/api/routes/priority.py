from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.schemas.priority import PriorityRequestSchema, PriorityResponseSchema, PriorityResultSchema
from app.intelligence.fusion.service import MultiIndicatorFusionService

router = APIRouter()

MOCK_PRIORITY_QUEUE = [
    {
        "id": "p_001",
        "rank": 1,
        "water_body": "Gosikhurd Reservoir",
        "zone": "Zone C",
        "date": "2026-09-22",
        "priority_score": 84,
        "severity": "HIGH",
        "confidence": 87,
        "primary_indicator": "NDTI",
        "investigation_status": "Prioritize for Ground Investigation",
    },
    {
        "id": "p_002",
        "rank": 2,
        "water_body": "Godavari River – Selected Segment",
        "zone": "Zone A",
        "date": "2026-09-21",
        "priority_score": 68,
        "severity": "MODERATE",
        "confidence": 82,
        "primary_indicator": "NDCI",
        "investigation_status": "Pending Analysis",
    }
]

@router.get("/")
def get_priority_queue() -> List[Dict[str, Any]]:
    return MOCK_PRIORITY_QUEUE

@router.post("/", response_model=PriorityResponseSchema)
def calculate_priority_endpoint(request: PriorityRequestSchema):
    """
    POST /api/priority endpoint for evidence fusion.
    """
    try:
        water_body_id = request.water_body_id
        scene_id = request.scene_id or "SENTINEL2_LIVE"
        acquisition_date = request.acquisition_date or "2026-09-22"

        zone_results_raw = []

        if request.anomaly_result:
            water_body_id = request.anomaly_result.get("water_body_id", water_body_id)
            scene_id = request.anomaly_result.get("scene_id", scene_id)
            acquisition_date = request.anomaly_result.get("acquisition_date", acquisition_date)
            
            if "results" in request.anomaly_result and isinstance(request.anomaly_result["results"], list):
                zone_results_raw = request.anomaly_result["results"]
            else:
                zone_results_raw = [request.anomaly_result]
        elif request.results:
            zone_results_raw = request.results

        if not zone_results_raw:
            zone_results_raw = [{
                "zone_id": "zone-main",
                "indicators": {},
                "statistical_anomaly": False,
                "combined_status": "NO_ANOMALY_SIGNAL",
                "quality": {"valid_percentage": 90.0}
            }]

        processed_zones = []
        for zone_data in zone_results_raw:
            z_id = zone_data.get("zone_id", "zone-main")
            res_trace = MultiIndicatorFusionService.process_zone_anomaly(
                water_body_id=water_body_id,
                zone_id=z_id,
                scene_id=scene_id,
                analysis_date=acquisition_date,
                zone_anomaly_data=zone_data
            )
            processed_zones.append(res_trace)

        processed_zones.sort(key=lambda x: x["investigation_priority_score"], reverse=True)

        return PriorityResponseSchema(
            water_body_id=water_body_id,
            scene_id=scene_id,
            acquisition_date=acquisition_date,
            results=[PriorityResultSchema(**z) for z in processed_zones]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Priority calculation failed: {exc}")
