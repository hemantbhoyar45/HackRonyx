import logging
from typing import Dict, List, Any
import ee

from .base import SpectralIndicator
from .ndti import NDTI
from .ndci import NDCI
from .fai import FAI
from .suspended_sediment import SuspendedSedimentProxy

logger = logging.getLogger(__name__)

# Registry of available indicators
AVAILABLE_INDICATORS: Dict[str, SpectralIndicator] = {
    "ndti": NDTI(),
    "ndci": NDCI(),
    "fai": FAI(),
    "suspended_sediment": SuspendedSedimentProxy()
}

def calculate_indicators(
    image: ee.Image, 
    water_mask: ee.Image, 
    aoi: ee.Geometry, 
    indicator_names: List[str],
    scale: int = 10
) -> Dict[str, Any]:
    """
    Calculates requested indicators over the detected water mask and computes statistics.
    Returns a dictionary of indicator statistics for the AOI.
    """
    results = {}
    
    # Restrict processing to valid pixels and detected water pixels
    masked_image = image.updateMask(water_mask)
    
    for name in indicator_names:
        if name not in AVAILABLE_INDICATORS:
            logger.warning(f"Indicator '{name}' is not registered. Skipping.")
            continue
            
        indicator = AVAILABLE_INDICATORS[name]
        
        try:
            # 1. Calculate Per-Pixel Raster
            ind_image = indicator.calculate(masked_image)
            
            # 2. Compute Statistics using ee.Reducer
            # We want mean, median, min, max, stdDev, and percentiles (10, 25, 75, 90)
            # Combine reducers for efficiency
            reducer = (
                ee.Reducer.mean()
                .combine(ee.Reducer.median(), '', True)
                .combine(ee.Reducer.minMax(), '', True)
                .combine(ee.Reducer.stdDev(), '', True)
                .combine(ee.Reducer.percentile([10, 25, 75, 90]), '', True)
                .combine(ee.Reducer.count(), '', True)
            )
            
            stats = ind_image.reduceRegion(
                reducer=reducer,
                geometry=aoi,
                scale=scale,
                maxPixels=1e9
            )
            
            # Fetch results
            stats_dict = stats.getInfo() or {}
            
            # 3. Format result
            band_name = ind_image.bandNames().get(0).getInfo()
            
            valid_count = stats_dict.get(f"{band_name}_count", 0)
            
            results[name] = {
                "indicator_name": name,
                "indicator_type": indicator.type,
                "formula": indicator.formula,
                "bands_used": indicator.bands_used,
                "units": indicator.units,
                "calibration_status": indicator.calibration_status,
                "statistics": {
                    "mean": stats_dict.get(f"{band_name}_mean", 0.0),
                    "median": stats_dict.get(f"{band_name}_median", 0.0),
                    "min": stats_dict.get(f"{band_name}_min", 0.0),
                    "max": stats_dict.get(f"{band_name}_max", 0.0),
                    "std": stats_dict.get(f"{band_name}_stdDev", 0.0),
                    "percentile_10": stats_dict.get(f"{band_name}_p10", 0.0),
                    "percentile_25": stats_dict.get(f"{band_name}_p25", 0.0),
                    "percentile_75": stats_dict.get(f"{band_name}_p75", 0.0),
                    "percentile_90": stats_dict.get(f"{band_name}_p90", 0.0),
                    "valid_pixel_count": int(valid_count)
                },
                "raster_image": ind_image # Keeping reference for map tiles later if needed
            }
            
        except Exception as e:
            logger.error(f"Error calculating indicator {name}: {e}")
            
    return results

def calculate_zone_indicators(
    image: ee.Image,
    water_mask: ee.Image,
    aoi: ee.Geometry,
    indicator_names: List[str],
    zones: ee.FeatureCollection = None,
    scale: int = 10
) -> List[Dict[str, Any]]:
    """
    Calculates indicators over predefined zones within the AOI.
    If no zones are provided, it can fall back to a grid or just return empty.
    For this MVP, we will just return a single default zone if none provided.
    """
    # For now, we will just treat the whole AOI as one zone (zone-main) to satisfy the schema requirement.
    # Future prompts will generate specific zones.
    
    zone_stats = calculate_indicators(image, water_mask, aoi, indicator_names, scale)
    
    # Collect valid_pixel_count from the first valid indicator to estimate total
    total_valid = 0
    if zone_stats:
        first_ind = list(zone_stats.values())[0]
        total_valid = first_ind["statistics"]["valid_pixel_count"]
    
    # Calculate water area for the zone
    pixel_area = ee.Image.pixelArea().multiply(water_mask)
    area_m2 = pixel_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    ).get('area').getInfo() or 0.0
    
    zone_results = [
        {
            "zone_id": "zone-main",
            "water_area_km2": area_m2 / 1_000_000.0,
            "valid_pixel_count": total_valid,
            "geometry": None, # Could include AOI geometry here
            "indicators": zone_stats
        }
    ]
    
    return zone_results
