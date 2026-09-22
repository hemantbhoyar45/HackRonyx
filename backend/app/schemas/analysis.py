from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class AnalysisRequest(BaseModel):
    water_body_id: str
    start_date: date
    end_date: date
    custom_aoi: Optional[dict] = None

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
