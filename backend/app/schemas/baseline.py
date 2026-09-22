"""
Pydantic schemas for Prompt 07 historical baseline API.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import date


class HistoricalRequest(BaseModel):
    water_body_id: str
    aoi: Optional[Dict[str, Any]] = None
    start_date: date
    end_date: date
    zone_id: str = "zone-main"
    max_cloud_pct: float = 30.0
    min_valid_water_pixels: int = 100


class HistoricalObservationSchema(BaseModel):
    scene_id: str
    acquisition_date: date
    sensor: str
    water_area_km2: float
    valid_pixel_count: int
    observation_status: str
    ndti_median: float
    ndci_median: float
    fai_median: float
    suspended_sediment_median: float


class TimeSeriesPoint(BaseModel):
    date: str
    scene_id: str
    median: float
    mean: float
    std: float
    observation_status: str


class HistoricalResponse(BaseModel):
    status: str
    data_source_mode: str = "live"
    water_body_id: str
    zone_id: str
    start_date: date
    end_date: date
    total_scenes_found: int
    valid_observations: int
    rejected_observations: int
    observations: List[HistoricalObservationSchema]
    time_series: Dict[str, List[TimeSeriesPoint]]
    message: str = ""


class BaselineRequest(BaseModel):
    water_body_id: str
    zone_id: str = "zone-main"
    indicator: str
    month: int = Field(..., ge=1, le=12)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BaselineStats(BaseModel):
    month: int
    observation_count: int
    median: Optional[float]
    mean: Optional[float]
    std: Optional[float]
    mad: Optional[float]
    p10: Optional[float]
    p25: Optional[float]
    p75: Optional[float]
    p90: Optional[float]
    baseline_status: str


class BaselineResponse(BaseModel):
    water_body_id: str
    zone_id: str
    indicator: str
    baseline: BaselineStats


class BaselineCompareRequest(BaseModel):
    water_body_id: str
    zone_id: str = "zone-main"
    indicator: str
    current_value: float
    current_date: date
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None


class DeviationResult(BaseModel):
    absolute: Optional[float]
    relative: Optional[float]
    robust: Optional[float]


class BaselineCompareResponse(BaseModel):
    water_body_id: str
    zone_id: str
    indicator: str
    current_value: float
    current_date: date
    baseline: BaselineStats
    deviation: DeviationResult
