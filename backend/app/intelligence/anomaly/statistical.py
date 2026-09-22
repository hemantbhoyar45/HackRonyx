from typing import Dict
from app.intelligence.anomaly.models import AnomalyFeature

def check_statistical_anomaly(
    features: Dict[str, AnomalyFeature], 
    robust_threshold: float = 3.0
) -> bool:
    """
    Checks if any of the indicators breach the configurable robust threshold.
    Returns True if an anomaly is detected statistically.
    """
    for indicator, feature in features.items():
        if abs(feature.robust_deviation) >= robust_threshold:
            return True
            
    return False
