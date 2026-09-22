from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class IndicatorStatistics(BaseModel):
    mean: float
    median: float
    min: float
    max: float
    std: float
    percentile_10: float
    percentile_25: float
    percentile_75: float
    percentile_90: float
    valid_pixel_count: int

class IndicatorResult(BaseModel):
    indicator_name: str
    indicator_type: str
    formula: str
    bands_used: List[str]
    units: str
    calibration_status: str
    statistics: IndicatorStatistics
    valid_percentage: float
    raster_reference: Optional[str] = None

class ZoneIndicatorResult(BaseModel):
    zone_id: str
    water_area_km2: float
    valid_pixel_count: int
    geometry: Optional[Dict[str, Any]] = None
    indicators: Dict[str, IndicatorResult]

class IndicatorsRequest(BaseModel):
    water_body_id: str
    scene_id: str
    aoi: Optional[Dict[str, Any]] = None
    indicators: List[str] = Field(default=["ndti", "suspended_sediment", "ndci", "fai"])
    water_mask_method: str = "combined"
    water_mask_threshold_method: str = "otsu"
    ndwi_threshold: Optional[float] = None
    mndwi_threshold: Optional[float] = None

class QualityMetadata(BaseModel):
    total_water_pixels: int
    acquisition_date: Optional[str] = None
    sensor: str = "Sentinel-2"
    scene_id: str
    water_body_id: str

class IndicatorsResponse(BaseModel):
    status: str
    message: str = ""
    data_source_mode: str = "live"
    quality_metadata: QualityMetadata
    global_indicators: Dict[str, IndicatorResult]
    zones: List[ZoneIndicatorResult]
