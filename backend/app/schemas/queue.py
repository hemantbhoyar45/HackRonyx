from pydantic import BaseModel
from typing import List, Optional, Any
from app.schemas.alert import AlertSchema

class PriorityQueueItem(BaseModel):
    rank: Optional[int] = None
    alert_id: str
    water_body_id: str
    zone_id: str
    scene_id: Optional[str] = None
    analysis_date: str

    investigation_priority_score: float
    priority_band: str

    severity: str
    confidence: float

    primary_driver: Optional[str] = None
    
    # We will reuse the full alert object as the underlying data, 
    # but the frontend might just use the QueueItem. Let's include
    # the original AlertSchema for full detail view context without
    # duplicating everything.
    alert_details: AlertSchema

    investigation_status: str
    updated_at: str
    created_at: str

class AlertStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None

class AlertStatusHistorySchema(BaseModel):
    id: str
    alert_id: str
    previous_status: str
    new_status: str
    changed_at: str
    changed_by: str
    reason: Optional[str] = None

class QueueResponseSchema(BaseModel):
    items: List[PriorityQueueItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class QueueSummarySchema(BaseModel):
    active: int
    acknowledged: int
    under_investigation: int
    resolved: int
    very_high_priority: int
    high_priority: int
