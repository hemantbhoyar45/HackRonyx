from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnomalyRequest(BaseModel):
    water_body_id: str
    scene_id: str
    current_date: str
    zones: List[str] = Field(default=["zone-main"])

class AnomalyFeatureSchema(BaseModel):
    indicator_name: str
    current_value: float
    baseline_median: float
    absolute_deviation: float
    relative_deviation: float
    robust_deviation: float
    valid_percentage: Optional[float] = None

class MLAnomalySchema(BaseModel):
    model: str
    status: str
    prediction: Optional[int] = None
    anomaly_score: Optional[float] = None

class AnomalyZoneResultSchema(BaseModel):
    zone_id: str
    indicators: Dict[str, AnomalyFeatureSchema]
    statistical_anomaly: bool
    statistical_threshold: float
    ml: MLAnomalySchema
    combined_status: str
    anomaly_score: float
    quality: Dict[str, float]
    affected_area: Optional[float] = None
    affected_percentage: Optional[float] = None

class AnomalyResponse(BaseModel):
    water_body_id: str
    scene_id: str
    acquisition_date: str
    results: List[AnomalyZoneResultSchema]
