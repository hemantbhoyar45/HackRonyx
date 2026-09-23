from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AlertEvidenceSchema(BaseModel):
    indicator: str
    description: str
    significance: str

class AlertActionRecommendationSchema(BaseModel):
    action: str
    urgency: str

class AlertSchema(BaseModel):
    alert_id: str
    water_body_id: str
    zone_id: str
    scene_id: str
    analysis_date: str
    
    title: str
    summary: str
    
    status: str = "ACTIVE"
    investigation_priority_score: float
    priority_band: str
    severity: str
    confidence: float
    
    primary_reason: str
    evidence_statements: List[AlertEvidenceSchema] = Field(default_factory=list)
    recommended_actions: List[AlertActionRecommendationSchema] = Field(default_factory=list)
    
    created_at: str
    updated_at: str

class AlertRequestSchema(BaseModel):
    # Expecting the output of Priority calculation
    water_body_id: str
    scene_id: str
    acquisition_date: str
    results: List[Dict[str, Any]]
    
class AlertResponseSchema(BaseModel):
    alerts: List[AlertSchema]
