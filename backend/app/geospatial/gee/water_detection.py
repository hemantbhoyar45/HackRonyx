import logging
from typing import Dict, Any, Tuple, Optional, List
import ee

logger = logging.getLogger(__name__)

# Typical fallback thresholds if Otsu fails or fixed is selected
DEFAULT_NDWI_THRESHOLD = 0.0
DEFAULT_MNDWI_THRESHOLD = 0.0
MIN_WATER_COMPONENT_PIXELS = 10  # Filter out noise < ~1000 sq meters at 10m scale

def calculate_ndwi(image: ee.Image) -> ee.Image:
    """NDWI = (Green - NIR) / (Green + NIR) -> (B3 - B8) / (B3 + B8)"""
    return image.normalizedDifference(['B3', 'B8']).rename('NDWI')

def calculate_mndwi(image: ee.Image) -> ee.Image:
    """MNDWI = (Green - SWIR) / (Green + SWIR) -> (B3 - B11) / (B3 + B11)"""
    return image.normalizedDifference(['B3', 'B11']).rename('MNDWI')

def get_histogram(index_image: ee.Image, aoi: ee.Geometry, scale: int = 10) -> List[Tuple[float, float]]:
    """
    Computes a fixed histogram of the index image within the AOI.
    Returns a list of [bucketMin, count] arrays.
    """
    # 256 buckets from -1 to 1
    histogram_reducer = ee.Reducer.fixedHistogram(-1.0, 1.0, 256)
    
    stats = index_image.reduceRegion(
        reducer=histogram_reducer,
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    )
    
    # Extract histogram array
    hist_array = stats.get(index_image.bandNames().get(0)).getInfo()
    
    if not hist_array:
        return []
        
    # Filter out empty buckets to reduce size
    return [[float(row[0]), float(row[1])] for row in hist_array if row[1] > 0]

def apply_water_mask(
    ndwi: ee.Image, 
    mndwi: ee.Image, 
    ndwi_thresh: Optional[float], 
    mndwi_thresh: Optional[float], 
    method: str = 'combined',
    min_pixels: int = MIN_WATER_COMPONENT_PIXELS
) -> ee.Image:
    """
    Applies the chosen thresholding strategy to create a binary water mask.
    1 = Water, 0 = Non-Water
    """
    if method == 'ndwi_fixed' or method == 'ndwi_otsu':
        t = ndwi_thresh if ndwi_thresh is not None else DEFAULT_NDWI_THRESHOLD
        mask = ndwi.gt(t)
    elif method == 'mndwi_fixed' or method == 'mndwi_otsu':
        t = mndwi_thresh if mndwi_thresh is not None else DEFAULT_MNDWI_THRESHOLD
        mask = mndwi.gt(t)
    else: # 'combined'
        t_n = ndwi_thresh if ndwi_thresh is not None else DEFAULT_NDWI_THRESHOLD
        t_m = mndwi_thresh if mndwi_thresh is not None else DEFAULT_MNDWI_THRESHOLD
        mask = ndwi.gt(t_n).And(mndwi.gt(t_m))
        
    # Clean up small objects using connectedPixelCount
    connected_count = mask.connectedPixelCount(min_pixels, True)
    
    # Only keep pixels that are both part of a large enough component AND belong to the original mask
    # unmask(0) ensures non-water becomes 0 instead of masked out
    # And(ndwi.mask()) restores the original quality/cloud mask boundaries
    clean_mask = mask.updateMask(connected_count.gte(min_pixels)).unmask(0).And(ndwi.mask())
    
    return clean_mask.rename('water_mask')

def calculate_water_stats(water_mask: ee.Image, aoi: ee.Geometry, scale: int = 10) -> Dict[str, float]:
    """
    Calculates AOI area and Water area using pixel area reducer.
    """
    pixel_area = ee.Image.pixelArea()
    
    # Total AOI Area (unmasked)
    aoi_area_res = pixel_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    ).get('area')
    
    # Water Area
    water_area_img = pixel_area.multiply(water_mask)
    water_area_res = water_area_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    ).get('area')
    
    aoi_m2 = aoi_area_res.getInfo() or 0.0
    water_m2 = water_area_res.getInfo() or 0.0
    
    aoi_km2 = aoi_m2 / 1_000_000.0
    water_km2 = water_m2 / 1_000_000.0
    
    coverage = (water_km2 / aoi_km2 * 100.0) if aoi_km2 > 0 else 0.0
    
    return {
        "aoi_area_km2": round(aoi_km2, 4),
        "water_area_km2": round(water_km2, 4),
        "water_coverage_percentage": round(coverage, 2)
    }

def vectorize_water_mask(water_mask: ee.Image, aoi: ee.Geometry, scale: int = 10) -> Dict[str, Any]:
    """
    Converts the binary water mask (1) into GeoJSON features.
    """
    # Only keep water pixels
    water_only = water_mask.selfMask()
    
    vectors = water_only.reduceToVectors(
        reducer=ee.Reducer.countEvery(),
        geometry=aoi,
        scale=scale,
        geometryType='polygon',
        eightConnected=False,
        maxPixels=1e9
    )
    
    try:
        geojson = vectors.getInfo()
        # Ensure it returns a FeatureCollection even if empty
        if not geojson or 'features' not in geojson:
            return {"type": "FeatureCollection", "features": []}
        return geojson
    except Exception as e:
        logger.error(f"Failed to vectorize water mask: {e}")
        return {"type": "FeatureCollection", "features": []}
