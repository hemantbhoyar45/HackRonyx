from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest
from typing import Dict, Any

router = APIRouter()

@router.post("/prepare")
def prepare_analysis(request: AnalysisRequest) -> Dict[str, Any]:
    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="Start date must be earlier than or equal to the end date.")
    
    # In a real app we'd validate the AOI geometry and prepare a job for Google Earth Engine.
    # For now, just return success.
    return {
        "status": "ready",
        "message": "Analysis request accepted",
        "water_body_id": request.water_body_id,
        "water_body_name": request.water_body_name,
        "start_date": str(request.start_date),
        "end_date": str(request.end_date)
    }
