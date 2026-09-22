from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class AnomalyFeature:
    indicator_name: str
    current_value: float
    baseline_median: float
    absolute_deviation: float
    relative_deviation: float
    robust_deviation: float
    valid_percentage: Optional[float] = None

@dataclass
class MLAnomalyResult:
    model: str
    status: str
    prediction: Optional[int] = None
    anomaly_score: Optional[float] = None

@dataclass
class AnomalyResult:
    water_body_id: str
    zone_id: str
    scene_id: str
    acquisition_date: str
    
    # Per-indicator features
    indicators: Dict[str, AnomalyFeature]
    
    # Statistical stage
    statistical_anomaly: bool
    statistical_threshold: float
    
    # ML stage
    ml: MLAnomalyResult
    
    # Combined
    combined_status: str
    anomaly_score: float
    
    # Quality and metadata
    quality: Dict[str, float]
    affected_area: Optional[float] = None
    affected_percentage: Optional[float] = None
