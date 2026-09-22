from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import date

class QualityMetadata(BaseModel):
    valid_pixel_percentage: float
    masked_pixel_percentage: float
    scene_cloud_percentage: Optional[float] = None
    cloud_mask_applied: bool = True
    shadow_mask_applied: bool = True
    snow_mask_applied: bool = True
    aoi_pixel_count: int
    valid_pixel_count: int
    quality_status: str

class PreprocessingRequest(BaseModel):
    scene_id: str
    water_body_id: str
    start_date: date
    end_date: date
    aoi: Dict[str, Any]

class PreprocessingResult(BaseModel):
    scene_id: str
    acquisition_date: Optional[str] = None
    satellite: str = "Sentinel-2"
    dataset: str = "COPERNICUS/S2_SR_HARMONIZED"
    aoi_id: str
    start_date: str
    end_date: str
    quality: QualityMetadata
    bands: List[str]
    bands_extended: List[str]
    reflectance_corrected: bool = True
    status: str
    data_source_mode: str
    message: str
