from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ReportGenerationRequest(BaseModel):
    report_type: str  # "ANALYSIS" | "INVESTIGATION"
    water_body_id: Optional[str] = None
    water_body_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    alert_id: Optional[str] = None
    scene_id: Optional[str] = None


class ReportMetadata(BaseModel):
    report_id: str
    report_type: str
    water_body_id: str
    water_body_name: str
    analysis_date: str
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    alert_id: Optional[str] = None
    generated_at: str
    processing_mode: str = "DEMO DATA"
    status: str = "READY"
    file_path: Optional[str] = None


class ReportPreviewSchema(BaseModel):
    report_id: str
    report_type: str
    water_body_id: str
    water_body_name: str
    analysis_date: str
    generated_at: str
    processing_mode: str
    status: str
    alert_id: Optional[str] = None

    # Executive summary data
    anomaly_detected: Optional[bool] = None
    priority_score: Optional[float] = None
    priority_band: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    primary_indicator: Optional[str] = None
    recommended_action: Optional[str] = None
