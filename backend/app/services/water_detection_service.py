import logging
from app.schemas.water_mask import WaterMaskRequest, WaterMaskResult, IndexMetadata
from app.geospatial.gee.client import is_gee_ready
from app.geospatial.gee.geometry import geojson_to_ee_geometry
from app.geospatial.gee.preprocessing import preprocess_scene
from app.geospatial.gee.water_detection import (
    calculate_ndwi, calculate_mndwi, get_histogram, 
    apply_water_mask, calculate_water_stats, vectorize_water_mask
)
from app.geospatial.water_detection.threshold import calculate_otsu_threshold

logger = logging.getLogger(__name__)

def run_water_detection(request: WaterMaskRequest) -> WaterMaskResult:
    logger.info(f"Water detection requested for scene={request.scene_id}, water_body={request.water_body_id}")
    
    if not is_gee_ready():
        return _demo_water_mask_response(request)
        
    try:
        ee_aoi = geojson_to_ee_geometry(request.aoi)
        
        # 1. Preprocess scene (reuse Prompt 04 logic internally)
        img, quality_stats = preprocess_scene(request.scene_id, ee_aoi)
        
        valid_pct = quality_stats.get("valid_pixel_percentage", 0)
        quality_status = "good"
        
        if valid_pct == 0:
            return WaterMaskResult(
                status="error",
                scene_id=request.scene_id,
                method=request.method,
                threshold_method=request.threshold_method,
                ndwi=IndexMetadata(available=False),
                mndwi=IndexMetadata(available=False),
                water_area_km2=0.0,
                aoi_area_km2=0.0,
                water_coverage_percentage=0.0,
                geometry={"type": "FeatureCollection", "features": []},
                quality_status="insufficient",
                message="No valid Sentinel-2 pixels remain inside the selected AOI after quality masking."
            )
        elif valid_pct < 10.0:
            quality_status = "low_quality"
            
        # 2. Calculate Indices
        ndwi = calculate_ndwi(img)
        mndwi = calculate_mndwi(img)
        
        # 3. Determine Thresholds
        t_ndwi = request.ndwi_threshold
        t_mndwi = request.mndwi_threshold
        
        if request.threshold_method == 'otsu':
            if 'ndwi' in request.method or request.method == 'combined':
                hist_ndwi = get_histogram(ndwi, ee_aoi)
                otsu_n = calculate_otsu_threshold(hist_ndwi)
                if otsu_n is not None:
                    t_ndwi = otsu_n
                    
            if 'mndwi' in request.method or request.method == 'combined':
                hist_mndwi = get_histogram(mndwi, ee_aoi)
                otsu_m = calculate_otsu_threshold(hist_mndwi)
                if otsu_m is not None:
                    t_mndwi = otsu_m
                    
        # 4. Generate Mask & Clean Up
        water_mask = apply_water_mask(
            ndwi=ndwi,
            mndwi=mndwi,
            ndwi_thresh=t_ndwi,
            mndwi_thresh=t_mndwi,
            method=request.method,
            min_pixels=request.min_component_pixels
        )
        
        # 5. Calculate Stats
        stats = calculate_water_stats(water_mask, ee_aoi)
        
        status = "success"
        message = "Water detection successful."
        if stats["water_area_km2"] == 0:
            status = "error"
            message = "No water pixels were detected inside the selected AOI."
            
        # 6. Vectorize Mask
        geometry = vectorize_water_mask(water_mask, ee_aoi)
        
        # Safeguard floating point drift
        water_area = stats["water_area_km2"]
        aoi_area = stats["aoi_area_km2"]
        if water_area > aoi_area:
            water_area = aoi_area
            
        return WaterMaskResult(
            status=status,
            scene_id=request.scene_id,
            method=request.method,
            threshold_method=request.threshold_method,
            ndwi=IndexMetadata(available=True, threshold=t_ndwi),
            mndwi=IndexMetadata(available=True, threshold=t_mndwi),
            water_area_km2=water_area,
            aoi_area_km2=aoi_area,
            water_coverage_percentage=stats["water_coverage_percentage"],
            geometry=geometry,
            quality_status=quality_status,
            message=message
        )
        
    except Exception as exc:
        logger.error(f"Water detection failed: {exc}")
        raise RuntimeError(f"Water detection failed: {exc}") from exc


def _demo_water_mask_response(request: WaterMaskRequest) -> WaterMaskResult:
    logger.info("Returning demo water mask data (GEE not connected).")
    
    # Very basic mock geometry
    mock_geometry = {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "properties": {},
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [79.5898, 20.8711],
                [79.6000, 20.8711],
                [79.6000, 20.8800],
                [79.5898, 20.8800],
                [79.5898, 20.8711]
              ]
            ]
          }
        }
      ]
    }
    
    return WaterMaskResult(
        status="success",
        scene_id=request.scene_id or "DEMO_SCENE",
        method=request.method,
        threshold_method=request.threshold_method,
        ndwi=IndexMetadata(available=True, threshold=0.12),
        mndwi=IndexMetadata(available=True, threshold=0.15),
        water_area_km2=2.5,
        aoi_area_km2=5.0,
        water_coverage_percentage=50.0,
        geometry=mock_geometry if "gosikhurd" in str(request.water_body_id) else {"type": "FeatureCollection", "features": []},
        quality_status="good",
        message="Demo water mask generated.",
        data_source_mode="demo"
    )
