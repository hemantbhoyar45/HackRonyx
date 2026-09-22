from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest
from app.schemas.preprocessing import PreprocessingRequest, PreprocessingResult
from app.services.analysis_service import run_scene_search
from app.services.preprocessing_service import run_preprocessing
from app.schemas.water_mask import WaterMaskRequest, WaterMaskResult
from app.services.water_detection_service import run_water_detection
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


@router.post("/scenes")
def search_satellite_scenes(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Search Sentinel-2 scenes for the given AOI and date range.

    Returns scene-level metadata. Does NOT download rasters or perform
    preprocessing — those belong to later prompts.
    """
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be earlier than or equal to the end date.",
        )

    aoi = request.custom_aoi or request.aoi
    if not aoi:
        raise HTTPException(status_code=400, detail="Invalid AOI geometry.")

    try:
        result = run_scene_search(
            water_body_id=request.water_body_id,
            water_body_name=request.water_body_name,
            aoi=aoi,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/preprocess", response_model=PreprocessingResult)
def preprocess_scene(request: PreprocessingRequest):
    """
    Execute the Sentinel-2 preprocessing pipeline:
    - Apply SCL mask (clouds, shadows, etc.)
    - Scale reflectance
    - Clip to AOI
    - Select bands
    - Compute quality metrics
    """
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be earlier than or equal to the end date.",
        )

    if not request.aoi:
        raise HTTPException(status_code=400, detail="Invalid AOI geometry.")
        
    if not request.scene_id:
        raise HTTPException(status_code=400, detail="Scene ID is required.")

    try:
        return run_preprocessing(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        # Avoid exposing stack traces
        raise HTTPException(status_code=500, detail="An unexpected error occurred during preprocessing.")


@router.post("/water-mask", response_model=WaterMaskResult)
def detect_water_mask(request: WaterMaskRequest):
    """
    Execute the Water Body Detection pipeline:
    - NDWI / MNDWI
    - Thresholding
    - Quality mask intersection
    - Vectorization
    """
    if not request.aoi:
        raise HTTPException(status_code=400, detail="Invalid AOI geometry.")
        
    if not request.scene_id:
        raise HTTPException(status_code=400, detail="Scene ID is required.")

    try:
        return run_water_detection(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred during water detection.")

