from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date


class AnalysisRequest(BaseModel):
    water_body_id: str
    water_body_name: str
    start_date: date
    end_date: date
    custom_aoi: Optional[Dict[str, Any]] = None
    aoi: Optional[Dict[str, Any]] = None


class SceneMetadata(BaseModel):
    scene_id: str
    acquisition_date: Optional[str] = None
    cloud_percentage: Optional[float] = None
    platform: Optional[str] = None
    product_id: Optional[str] = None
    processing_baseline: Optional[str] = None


class SceneSearchResponse(BaseModel):
    analysis_id: str
    status: str  # "scenes_found" | "no_data" | "error"
    data_source_mode: str  # "live" | "demo"
    provider: str
    source: str
    collection: str
    water_body_id: str
    water_body_name: Optional[str] = None
    start_date: str
    end_date: str
    max_cloud_percent: float
    scene_count: int
    scenes: List[SceneMetadata]
    message: str


class IndicatorResult(BaseModel):
    name: str
    value: float
    unit: str
    status: str


class AnalysisResult(BaseModel):
    id: str
    water_body_id: str
    date_analyzed: date
    indicators: List[IndicatorResult]
    anomaly_detected: bool
    priority_score: int
    confidence: int

