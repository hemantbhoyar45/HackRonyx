"""
Approved Earth Engine collection constants.

Keep all collection IDs in one place so they are never scattered across
the codebase.  Future collections (e.g. Landsat 8/9) can be added here.
"""

# Primary Sentinel-2 Surface Reflectance collection for the MVP
SENTINEL2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

# Default maximum scene-level cloud cover percentage (configurable)
import os

MAX_SCENE_CLOUD_PERCENT: float = float(
    os.getenv("MAX_SCENE_CLOUD_PERCENT", "30")
)

# Minimum acceptable valid pixel percentage after masking
MIN_VALID_PIXEL_PERCENTAGE: float = float(
    os.getenv("MIN_VALID_PIXEL_PERCENTAGE", "50")
)

# Core analysis bands
CORE_BANDS = ["B2", "B3", "B4", "B8", "B11", "B12"]

# Extended bands (includes red-edge for future chlorophyll/algal analysis)
EXTENDED_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]

# SCL classes to mask as invalid
# 0: No data
# 1: Saturated/defective
# 3: Cloud shadow
# 8: Cloud medium probability
# 9: Cloud high probability
# 10: Thin cirrus
# 11: Snow/ice
SCL_MASK_VALUES = [0, 1, 3, 8, 9, 10, 11]
