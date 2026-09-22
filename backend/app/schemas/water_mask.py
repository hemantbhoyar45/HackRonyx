from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class WaterMaskRequest(BaseModel):
    scene_id: str
    water_body_id: str
    aoi: Optional[Dict[str, Any]] = None
    method: str = Field(
        default="combined", 
        description="Supported values: ndwi_fixed, mndwi_fixed, ndwi_otsu, mndwi_otsu, combined"
    )
    threshold_method: str = Field(default="otsu", description="otsu or fixed")
    ndwi_threshold: Optional[float] = None
    mndwi_threshold: Optional[float] = None
    min_component_pixels: int = 10

class IndexMetadata(BaseModel):
    available: bool
    threshold: Optional[float] = None

class WaterMaskResult(BaseModel):
    status: str
    scene_id: str
    method: str
    threshold_method: str
    ndwi: IndexMetadata
    mndwi: IndexMetadata
    water_area_km2: float
    aoi_area_km2: float
    water_coverage_percentage: float
    geometry: Dict[str, Any]
    quality_status: Optional[str] = None
    message: str = ""
    data_source_mode: str = "live"
