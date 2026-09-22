from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest
from app.schemas.preprocessing import PreprocessingRequest, PreprocessingResult
from app.services.analysis_service import run_scene_search
from app.services.preprocessing_service import run_preprocessing
from app.schemas.water_mask import WaterMaskRequest, WaterMaskResult
from app.services.water_detection_service import run_water_detection
from app.schemas.indicators import IndicatorsRequest, IndicatorsResponse
from app.services.indicator_service import run_indicators
from app.schemas.baseline import (
    HistoricalRequest, HistoricalResponse,
    BaselineRequest, BaselineResponse,
    BaselineCompareRequest, BaselineCompareResponse,
)
from app.services.historical_service import (
    run_historical, run_get_baseline, run_compare_baseline,
)
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


@router.post("/indicators", response_model=IndicatorsResponse)
def compute_indicators(request: IndicatorsRequest):
    """
    Execute the Spectral Indicator Engine:
    - Calculates NDTI, NDCI, FAI, Suspended Sediment Proxy
    - Restricts calculation strictly to valid + water pixels
    - Returns median, mean, std, and percentiles for AOI/Zones
    """
    if not request.aoi:
        raise HTTPException(status_code=400, detail="Invalid AOI geometry.")
        
    if not request.scene_id:
        raise HTTPException(status_code=400, detail="Scene ID is required.")

    try:
        return run_indicators(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred during indicator calculation.")


# ──────────────────────────────────────────────────────────────
#  Prompt 07 — Historical Baseline & Time-Series
# ──────────────────────────────────────────────────────────────

@router.post("/historical", response_model=HistoricalResponse)
def historical_observations(request: HistoricalRequest):
    """
    Retrieve (or generate demo) historical Sentinel-2 observations for a water body.
    Persists observations to the baseline repository and returns indicator time-series.
    """
    try:
        return run_historical(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Historical analysis failed: {exc}")


@router.post("/baseline", response_model=BaselineResponse)
def get_indicator_baseline(request: BaselineRequest):
    """
    Compute seasonal (month-of-year) baseline statistics for a single indicator.
    Returns median, MAD, percentile band, and baseline status.
    """
    try:
        return run_get_baseline(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Baseline computation failed: {exc}")


@router.post("/baseline/compare", response_model=BaselineCompareResponse)
def compare_with_baseline(request: BaselineCompareRequest):
    """
    Compare a single current indicator value against its seasonal baseline.
    Returns absolute, relative, and MAD-normalized (robust) deviations.
    """
    try:
        return run_compare_baseline(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Baseline comparison failed: {exc}")

