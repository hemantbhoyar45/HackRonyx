from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class IndicatorEvidenceSchema(BaseModel):
    indicator_name: str
    current_value: Optional[float] = None
    baseline_value: Optional[float] = None
    absolute_deviation: Optional[float] = None
    relative_deviation: Optional[float] = None
    robust_deviation: Optional[float] = None
    direction: str = "UNKNOWN"
    evidence_score: float
    weight: float
    weighted_contribution: float
    available: bool = True

class PriorityResultSchema(BaseModel):
    water_body_id: str
    zone_id: str
    scene_id: str
    analysis_date: str
    combined_status: Optional[str] = "POTENTIAL_ANOMALY"
    combined_evidence: float
    indicator_agreement_score: float
    quality_factor: float
    indicator_completeness: float
    historical_support: float
    model_agreement_score: Optional[float] = None
    severity: str
    severity_normalized: Optional[float] = None
    confidence: float
    confidence_normalized: Optional[float] = None
    investigation_priority_score: float
    priority_band: str
    primary_driver: Optional[str] = None
    supporting_indicators: List[str] = Field(default_factory=list)
    indicators: List[IndicatorEvidenceSchema] = Field(default_factory=list)
    evidence_trace: Optional[Dict[str, Any]] = None
    affected_area: Optional[float] = 0.0

class PriorityRequestSchema(BaseModel):
    water_body_id: str
    scene_id: Optional[str] = "SENTINEL2_LIVE"
    acquisition_date: Optional[str] = "2026-09-22"
    anomaly_result: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None

class PriorityResponseSchema(BaseModel):
    water_body_id: str
    scene_id: str
    acquisition_date: str
    results: List[PriorityResultSchema]
