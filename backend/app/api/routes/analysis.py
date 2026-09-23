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
from app.schemas.anomaly import AnomalyRequest, AnomalyResponse
from app.services.historical_service import (
    run_historical, run_get_baseline, run_compare_baseline,
)
from app.services.anomaly_service import AnomalyService
from typing import Dict, Any

router = APIRouter()
anomaly_service = AnomalyService()


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

# ──────────────────────────────────────────────────────────────
#  Prompt 08 — AI Anomaly Detection Engine
# ──────────────────────────────────────────────────────────────

@router.post("/anomaly", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    """
    Execute AI anomaly detection using two-stage robust statistical dev + Isolation Forest.
    """
    try:
        return await anomaly_service.detect_anomalies(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {exc}")


# ──────────────────────────────────────────────────────────────
#  Prompt 09 — Multi-Indicator Evidence Fusion & Priority Score
# ──────────────────────────────────────────────────────────────

from app.schemas.priority import PriorityRequestSchema, PriorityResponseSchema, PriorityResultSchema
from app.intelligence.fusion.service import MultiIndicatorFusionService

@router.post("/priority", response_model=PriorityResponseSchema)
def calculate_priority(request: PriorityRequestSchema):
    """
    Execute Multi-Indicator Evidence Fusion & Investigation Priority Scoring.
    Consumes Prompt 08 Anomaly detection results.
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

        # Fallback if no zone results were provided in request: create default zone structure
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

        # Sort multi-zone results by investigation_priority_score DESC
        processed_zones.sort(key=lambda x: x["investigation_priority_score"], reverse=True)

        return PriorityResponseSchema(
            water_body_id=water_body_id,
            scene_id=scene_id,
            acquisition_date=acquisition_date,
            results=[PriorityResultSchema(**z) for z in processed_zones]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Priority calculation failed: {exc}")


# ──────────────────────────────────────────────────────────────
#  Prompt 10 — Explainability & Alert System
# ──────────────────────────────────────────────────────────────

from app.schemas.alert import AlertRequestSchema, AlertResponseSchema
from app.intelligence.explainability.service import ExplainabilityService
from app.database.repositories.alert_repository import AlertRepository

@router.post("/alert", response_model=AlertResponseSchema)
def generate_alerts(request: AlertRequestSchema):
    """
    Execute Explainability & Alert System to deterministically convert Priority results
    into actionable natural language alerts.
    """
    try:
        alerts = ExplainabilityService.generate_alerts(request.results)
        
        # Persist alerts to repository
        repo = AlertRepository()
        for alert in alerts:
            repo.save_alert(alert.model_dump())
            
        return AlertResponseSchema(alerts=alerts)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Alert generation failed: {exc}")



