import logging
from typing import Any, Dict
from datetime import date

from app.geospatial.gee.client import is_gee_ready
from app.geospatial.gee.geometry import geojson_to_ee_geometry
from app.geospatial.gee.collections import MIN_VALID_PIXEL_PERCENTAGE, CORE_BANDS, EXTENDED_BANDS
from app.geospatial.gee.preprocessing import preprocess_scene
from app.schemas.preprocessing import PreprocessingRequest, PreprocessingResult, QualityMetadata

logger = logging.getLogger(__name__)


def run_preprocessing(request: PreprocessingRequest) -> PreprocessingResult:
    """
    Executes the preprocessing pipeline for a given Sentinel-2 scene.
    """
    logger.info("Preprocessing requested for scene=%s, water_body=%s", request.scene_id, request.water_body_id)
    
    if not request.scene_id:
        raise ValueError("Scene ID is required for preprocessing.")
        
    if not is_gee_ready():
        return _demo_preprocessing_response(request)
        
    try:
        ee_aoi = geojson_to_ee_geometry(request.aoi)
        
        scene_id = request.scene_id
        
        # 1. Preprocess scene using GEE (server-side)
        _, quality_stats = preprocess_scene(scene_id, ee_aoi)
        
        valid_pct = quality_stats.get("valid_pixel_percentage", 0)
        
        status = "success"
        message = "Preprocessing completed successfully."
        quality_status = "good"
        
        # 2. Quality validation
        if valid_pct == 0:
            status = "error"
            quality_status = "insufficient"
            message = "No valid Sentinel-2 pixels remain inside the selected AOI after quality masking."
        elif valid_pct < MIN_VALID_PIXEL_PERCENTAGE:
            status = "low_quality"
            quality_status = "low_quality"
            message = f"Valid pixel percentage ({valid_pct}%) is below the minimum threshold ({MIN_VALID_PIXEL_PERCENTAGE}%)."
            
        # Parse approximate acquisition date from Scene ID (e.g., COPERNICUS/S2_SR_HARMONIZED/20260115T053131_20260115T054321_T44QNF)
        date_str = None
        parts = scene_id.split('/')
        if len(parts) > 2:
            id_part = parts[-1]
            date_str_raw = id_part.split('_')[0]
            if len(date_str_raw) >= 8:
                date_str = f"{date_str_raw[:4]}-{date_str_raw[4:6]}-{date_str_raw[6:8]}"
        
        # 3. Compile Quality Metadata
        quality = QualityMetadata(
            valid_pixel_percentage=valid_pct,
            masked_pixel_percentage=quality_stats.get("masked_pixel_percentage", 0),
            scene_cloud_percentage=None, # Usually passed from upstream search result
            cloud_mask_applied=True,
            shadow_mask_applied=True,
            snow_mask_applied=True,
            aoi_pixel_count=quality_stats.get("aoi_pixel_count", 0),
            valid_pixel_count=quality_stats.get("valid_pixel_count", 0),
            quality_status=quality_status,
        )
        
        # 4. Construct response
        return PreprocessingResult(
            scene_id=scene_id,
            acquisition_date=date_str,
            satellite="Sentinel-2",
            dataset="COPERNICUS/S2_SR_HARMONIZED",
            aoi_id=request.water_body_id,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            quality=quality,
            bands=CORE_BANDS,
            bands_extended=EXTENDED_BANDS,
            reflectance_corrected=True,
            status=status,
            data_source_mode="live",
            message=message
        )
        
    except ValueError as exc:
        raise
    except Exception as exc:
        logger.error("Preprocessing service failed: %s", exc)
        raise RuntimeError("Google Earth Engine preprocessing failed.") from exc


def _demo_preprocessing_response(request: PreprocessingRequest) -> PreprocessingResult:
    """Return clearly labelled demo data when GEE is not connected."""
    logger.info("Returning demo preprocessing data (GEE not connected).")
    
    quality = QualityMetadata(
        valid_pixel_percentage=92.4,
        masked_pixel_percentage=7.6,
        scene_cloud_percentage=8.4,
        cloud_mask_applied=True,
        shadow_mask_applied=True,
        snow_mask_applied=True,
        aoi_pixel_count=15420,
        valid_pixel_count=14248,
        quality_status="good",
    )
    
    # Generate mock date from scene_id if possible
    acq_date = "2026-01-15"
    if "DEMO_S2" in request.scene_id and len(request.scene_id) > 17:
        # e.g., DEMO_S2A_20260115T053131...
        ds = request.scene_id[9:17]
        acq_date = f"{ds[:4]}-{ds[4:6]}-{ds[6:8]}"

    return PreprocessingResult(
        scene_id=request.scene_id or "DEMO_S2A_20260115T053131_N0400_R005_T44QNF",
        acquisition_date=acq_date,
        satellite="Sentinel-2",
        dataset="COPERNICUS/S2_SR_HARMONIZED",
        aoi_id=request.water_body_id,
        start_date=str(request.start_date),
        end_date=str(request.end_date),
        quality=quality,
        bands=CORE_BANDS,
        bands_extended=EXTENDED_BANDS,
        reflectance_corrected=True,
        status="success",
        data_source_mode="demo",
        message="Demo preprocessing complete — Google Earth Engine is not connected."
    )
