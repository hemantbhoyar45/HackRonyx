import logging
from typing import Any, Dict, List, Tuple

import ee

from app.geospatial.gee.collections import EXTENDED_BANDS, SCL_MASK_VALUES

logger = logging.getLogger(__name__)


def apply_scl_mask(image: ee.Image) -> ee.Image:
    """
    Apply Sentinel-2 Scene Classification Layer (SCL) mask.
    Masks out clouds, shadows, cirrus, snow/ice, and no-data/saturated pixels.
    """
    scl = image.select("SCL")
    
    # Create mask where SCL is NOT in the list of masked values
    # Start with all 1s (valid)
    mask = ee.Image(1)
    
    # Mask out each invalid class
    for invalid_class in SCL_MASK_VALUES:
        mask = mask.And(scl.neq(invalid_class))
        
    return image.updateMask(mask)


def apply_reflectance_scaling(image: ee.Image) -> ee.Image:
    """
    Apply Sentinel-2 harmonized offset and scale correction.
    S2_SR_HARMONIZED uses QUANTIFICATION_VALUE=10000 and adds a RADIO_ADD_OFFSET of -1000
    for scenes processed with newer baseline. The HARMONIZED collection shifts older data
    to match the new baseline, so we simply multiply by 0.0001 to get physical reflectance.
    """
    # Bands to scale (B1 to B12, B8A)
    bands_to_scale = image.bandNames().filter(ee.Filter.stringStartsWith("item", "B"))
    
    # Select only the optical bands to scale
    optical_bands = image.select(bands_to_scale)
    
    # Multiply by 0.0001 (1/10000) for physical reflectance (0.0 to 1.0+)
    scaled = optical_bands.multiply(0.0001)
    
    # Add the scaled bands back to the image, overwriting the unscaled ones
    return image.addBands(scaled, overwrite=True)


def select_analysis_bands(image: ee.Image, bands: List[str] = EXTENDED_BANDS) -> ee.Image:
    """Select core and extended bands for downstream analysis."""
    return image.select(bands)


def compute_quality_stats(image: ee.Image, ee_aoi: ee.Geometry) -> Dict[str, Any]:
    """
    Compute quality statistics server-side in Earth Engine using reduceRegion.
    Counts total pixels and valid pixels within the AOI.
    """
    # Use B3 (Green) as reference for valid pixel counts.
    # The mask applied earlier will carry over.
    valid_pixels_img = ee.Image(1).updateMask(image.select('B3').mask())
    
    # To count total pixels, we use an unmasked 1s image
    total_pixels_img = ee.Image(1)
    
    # Scale to count pixels approx natively (~10m for B3)
    scale = 10
    
    # Compute valid pixels
    valid_count = valid_pixels_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=ee_aoi,
        scale=scale,
        maxPixels=1e9
    ).get('constant')
    
    # Compute total pixels
    total_count = total_pixels_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=ee_aoi,
        scale=scale,
        maxPixels=1e9
    ).get('constant')
    
    # Retrieve values client-side
    valid = valid_count.getInfo() or 0
    total = total_count.getInfo() or 0
    
    if total == 0:
        return {
            "aoi_pixel_count": 0,
            "valid_pixel_count": 0,
            "valid_pixel_percentage": 0.0,
            "masked_pixel_percentage": 100.0,
        }
        
    valid_pct = (valid / total) * 100.0
    masked_pct = 100.0 - valid_pct
    
    return {
        "aoi_pixel_count": int(total),
        "valid_pixel_count": int(valid),
        "valid_pixel_percentage": round(valid_pct, 2),
        "masked_pixel_percentage": round(masked_pct, 2),
    }


def preprocess_scene(scene_id: str, ee_aoi: ee.Geometry) -> Tuple[ee.Image, Dict[str, Any]]:
    """
    Orchestrator: loads image -> applies SCL mask -> scales reflectance -> 
    clips to AOI -> selects bands -> computes quality stats.
    
    Returns the preprocessed Earth Engine Image and the computed quality metadata dict.
    """
    logger.info("Starting preprocessing for scene: %s", scene_id)
    
    try:
        # Load the image
        img = ee.Image(scene_id)
        
        # 1. Apply SCL mask
        masked_img = apply_scl_mask(img)
        
        # 2. Scale reflectance
        scaled_img = apply_reflectance_scaling(masked_img)
        
        # 3. Clip to AOI
        clipped_img = scaled_img.clip(ee_aoi)
        
        # 4. Compute quality stats before band selection (uses B3)
        quality_stats = compute_quality_stats(clipped_img, ee_aoi)
        
        # 5. Select analysis bands
        final_img = select_analysis_bands(clipped_img)
        
        return final_img, quality_stats
        
    except Exception as exc:
        logger.error("Preprocessing failed for %s: %s", scene_id, exc)
        raise RuntimeError(f"Earth Engine preprocessing failed: {exc}") from exc
