import math
from typing import Dict, Any, Optional
from app.intelligence.anomaly.models import AnomalyFeature

def compute_robust_deviation(current_value: float, median: float, mad: float, epsilon: float = 1e-6) -> float:
    """
    Compute robust deviation: (current_value - baseline_median) / MAD.
    Handles MAD == 0 by using epsilon.
    """
    # Protect against NaN/Inf
    if math.isnan(current_value) or math.isnan(median) or math.isnan(mad):
        return 0.0
        
    effective_mad = mad if mad > epsilon else epsilon
    robust_dev = (current_value - median) / effective_mad
    
    # Cap to prevent extreme values if MAD was artificially small
    return max(min(robust_dev, 100.0), -100.0)

def extract_features(
    indicator_name: str, 
    current_stats: Dict[str, Any], 
    baseline_stats: Optional[Dict[str, Any]]
) -> AnomalyFeature:
    """
    Extracts features for a single indicator comparing current against baseline.
    """
    current_val = current_stats.get("mean", 0.0)
    valid_perc = current_stats.get("valid_pixel_percentage", None)
    
    if not baseline_stats:
        return AnomalyFeature(
            indicator_name=indicator_name,
            current_value=current_val,
            baseline_median=0.0,
            absolute_deviation=0.0,
            relative_deviation=0.0,
            robust_deviation=0.0,
            valid_percentage=valid_perc
        )
        
    median = baseline_stats.get("median", 0.0)
    mad = baseline_stats.get("mad", 0.0)
    
    abs_dev = current_val - median
    rel_dev = (abs_dev / median) if abs(median) > 1e-6 else 0.0
    robust_dev = compute_robust_deviation(current_val, median, mad)
    
    return AnomalyFeature(
        indicator_name=indicator_name,
        current_value=current_val,
        baseline_median=median,
        absolute_deviation=abs_dev,
        relative_deviation=rel_dev,
        robust_deviation=robust_dev,
        valid_percentage=valid_perc
    )
