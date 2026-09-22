import logging
from typing import Dict, Any, List

from app.schemas.indicators import (
    IndicatorsRequest, IndicatorsResponse, QualityMetadata, 
    IndicatorResult, ZoneIndicatorResult, IndicatorStatistics
)
from app.geospatial.gee.client import is_gee_ready
from app.geospatial.gee.geometry import geojson_to_ee_geometry
from app.geospatial.gee.preprocessing import preprocess_scene
from app.geospatial.gee.water_detection import calculate_ndwi, calculate_mndwi, get_histogram, apply_water_mask
from app.geospatial.water_detection.threshold import calculate_otsu_threshold
from app.geospatial.indicators.engine import calculate_indicators, calculate_zone_indicators

logger = logging.getLogger(__name__)

def run_indicators(request: IndicatorsRequest) -> IndicatorsResponse:
    logger.info(f"Spectral indicators requested for scene={request.scene_id}, water_body={request.water_body_id}")
    
    if not is_gee_ready():
        return _demo_indicators_response(request)
        
    try:
        ee_aoi = geojson_to_ee_geometry(request.aoi)
        
        # 1. Preprocess scene (reuse Prompt 04 logic)
        img, quality_stats = preprocess_scene(request.scene_id, ee_aoi)
        
        valid_pct = quality_stats.get("valid_pixel_percentage", 0)
        if valid_pct == 0:
            raise RuntimeError("No valid pixels remain after quality masking for this scene.")
            
        # 2. Re-create Water Mask (reuse Prompt 05 logic)
        ndwi = calculate_ndwi(img)
        mndwi = calculate_mndwi(img)
        
        t_ndwi = request.ndwi_threshold
        t_mndwi = request.mndwi_threshold
        
        if request.water_mask_threshold_method == 'otsu':
            if 'ndwi' in request.water_mask_method or request.water_mask_method == 'combined':
                hist_ndwi = get_histogram(ndwi, ee_aoi)
                otsu_n = calculate_otsu_threshold(hist_ndwi)
                if otsu_n is not None:
                    t_ndwi = otsu_n
                    
            if 'mndwi' in request.water_mask_method or request.water_mask_method == 'combined':
                hist_mndwi = get_histogram(mndwi, ee_aoi)
                otsu_m = calculate_otsu_threshold(hist_mndwi)
                if otsu_m is not None:
                    t_mndwi = otsu_m
                    
        water_mask = apply_water_mask(
            ndwi=ndwi,
            mndwi=mndwi,
            ndwi_thresh=t_ndwi,
            mndwi_thresh=t_mndwi,
            method=request.water_mask_method
        )
        
        # 3. Calculate Global Indicators & Statistics
        global_stats_raw = calculate_indicators(img, water_mask, ee_aoi, request.indicators)
        
        # Format for response (removing raster_image from dict to schema)
        global_indicators = {}
        max_valid_pixels = 0
        
        for name, data in global_stats_raw.items():
            valid_pixels = data["statistics"].get("valid_pixel_count", 0)
            max_valid_pixels = max(max_valid_pixels, valid_pixels)
            
            # Estimate valid percentage based on a rough 10m pixel size area estimation if needed, 
            # but we just keep it simple or relative to total valid water pixels
            
            # Map dict to Pydantic model
            stats_model = IndicatorStatistics(**data["statistics"])
            
            # We don't send raster images over JSON, we'd generate a map tile URL if this was full production.
            # For this prompt we just return the stats.
            global_indicators[name] = IndicatorResult(
                indicator_name=data["indicator_name"],
                indicator_type=data["indicator_type"],
                formula=data["formula"],
                bands_used=data["bands_used"],
                units=data["units"],
                calibration_status=data["calibration_status"],
                statistics=stats_model,
                valid_percentage=100.0, # Placeholder, would compare to total water pixels
                raster_reference=f"{request.scene_id}_{name}" 
            )
            
        if max_valid_pixels == 0:
            raise RuntimeError("No valid water pixels available for spectral indicator calculation.")
            
        # 4. Calculate Zone Indicators
        zones_raw = calculate_zone_indicators(img, water_mask, ee_aoi, request.indicators)
        zones = []
        for z_data in zones_raw:
            z_indicators = {}
            for name, data in z_data["indicators"].items():
                z_indicators[name] = IndicatorResult(
                    indicator_name=data["indicator_name"],
                    indicator_type=data["indicator_type"],
                    formula=data["formula"],
                    bands_used=data["bands_used"],
                    units=data["units"],
                    calibration_status=data["calibration_status"],
                    statistics=IndicatorStatistics(**data["statistics"]),
                    valid_percentage=100.0,
                    raster_reference=f"{request.scene_id}_{name}_zone"
                )
                
            zones.append(ZoneIndicatorResult(
                zone_id=z_data["zone_id"],
                water_area_km2=z_data["water_area_km2"],
                valid_pixel_count=z_data["valid_pixel_count"],
                geometry=z_data["geometry"],
                indicators=z_indicators
            ))

        # 5. Construct Quality Metadata
        metadata = QualityMetadata(
            total_water_pixels=max_valid_pixels,
            scene_id=request.scene_id,
            water_body_id=request.water_body_id
        )

        return IndicatorsResponse(
            status="success",
            message="Spectral indicators calculated successfully.",
            data_source_mode="live",
            quality_metadata=metadata,
            global_indicators=global_indicators,
            zones=zones
        )
        
    except Exception as exc:
        logger.error(f"Indicator calculation failed: {exc}")
        raise RuntimeError(f"Indicator calculation failed: {exc}") from exc


def _demo_indicators_response(request: IndicatorsRequest) -> IndicatorsResponse:
    logger.info("Returning demo spectral indicators data (GEE not connected).")
    
    global_indicators = {}
    
    if "ndti" in request.indicators:
        global_indicators["ndti"] = IndicatorResult(
            indicator_name="ndti",
            indicator_type="Turbidity-Related Indicator",
            formula="(B4 - B3) / (B4 + B3)",
            bands_used=["B3", "B4"],
            units="relative / dimensionless proxy",
            calibration_status="not_calibrated",
            statistics=IndicatorStatistics(
                mean=0.12, median=0.11, min=-0.05, max=0.35, std=0.04,
                percentile_10=0.05, percentile_25=0.08, percentile_75=0.15, percentile_90=0.18,
                valid_pixel_count=15420
            ),
            valid_percentage=98.5,
            raster_reference="demo_ndti"
        )
        
    if "suspended_sediment" in request.indicators:
        global_indicators["suspended_sediment"] = IndicatorResult(
            indicator_name="suspended_sediment",
            indicator_type="Suspended Sediment Proxy",
            formula="(B4 - B2) / (B4 + B2)",
            bands_used=["B2", "B4"],
            units="relative / dimensionless proxy",
            calibration_status="not_calibrated",
            statistics=IndicatorStatistics(
                mean=0.18, median=0.17, min=0.01, max=0.45, std=0.06,
                percentile_10=0.10, percentile_25=0.14, percentile_75=0.22, percentile_90=0.27,
                valid_pixel_count=15420
            ),
            valid_percentage=98.5,
            raster_reference="demo_suspended_sediment"
        )
        
    if "ndci" in request.indicators:
        global_indicators["ndci"] = IndicatorResult(
            indicator_name="ndci",
            indicator_type="Chlorophyll-Related Indicator",
            formula="(B5 - B4) / (B5 + B4)",
            bands_used=["B4", "B5"],
            units="relative / dimensionless proxy",
            calibration_status="not_calibrated",
            statistics=IndicatorStatistics(
                mean=0.08, median=0.07, min=-0.1, max=0.25, std=0.03,
                percentile_10=0.04, percentile_25=0.05, percentile_75=0.10, percentile_90=0.12,
                valid_pixel_count=15420
            ),
            valid_percentage=98.5,
            raster_reference="demo_ndci"
        )
        
    if "fai" in request.indicators:
        global_indicators["fai"] = IndicatorResult(
            indicator_name="fai",
            indicator_type="Algal Activity-Related Indicator",
            formula="B8 - (B4 + (B11 - B4) * ((842 - 665) / (1610 - 665)))",
            bands_used=["B4", "B8", "B11"],
            units="relative / dimensionless proxy",
            calibration_status="not_calibrated",
            statistics=IndicatorStatistics(
                mean=0.015, median=0.012, min=-0.05, max=0.08, std=0.01,
                percentile_10=-0.01, percentile_25=0.005, percentile_75=0.025, percentile_90=0.04,
                valid_pixel_count=15420
            ),
            valid_percentage=98.5,
            raster_reference="demo_fai"
        )
        
    zones = [
        ZoneIndicatorResult(
            zone_id="zone-main",
            water_area_km2=2.5,
            valid_pixel_count=15420,
            geometry=None,
            indicators=global_indicators
        )
    ]
    
    metadata = QualityMetadata(
        total_water_pixels=15420,
        scene_id=request.scene_id or "DEMO_SCENE",
        water_body_id=request.water_body_id
    )

    return IndicatorsResponse(
        status="success",
        message="Demo indicators generated.",
        data_source_mode="demo",
        quality_metadata=metadata,
        global_indicators=global_indicators,
        zones=zones
    )
