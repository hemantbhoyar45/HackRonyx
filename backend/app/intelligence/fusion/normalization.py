import math
from typing import Optional

def normalize_robust_deviation(
    robust_dev: Optional[float],
    threshold: float = 3.0
) -> float:
    """
    Normalizes a robust deviation (e.g., MAD Z-score) into a 0.0 to 1.0 evidence score.
    
    Formula concept:
    - 0 deviation -> evidence = 0.0
    - threshold deviation -> evidence ~ 0.8
    - > threshold -> capped smoothly at 1.0
    
    Handles NaN, infinity, None, and negative deviations safely.
    """
    if robust_dev is None:
        return 0.0
        
    try:
        val = float(robust_dev)
    except (ValueError, TypeError):
        return 0.0
        
    if math.isnan(val) or math.isinf(val):
        return 0.0
        
    abs_dev = abs(val)
    if abs_dev <= 0.0:
        return 0.0
        
    if threshold <= 0:
        threshold = 3.0
        
    # Non-linear smooth scaling: using smooth saturation
    # At abs_dev = 0 -> 0.0
    # At abs_dev = threshold -> 0.8
    # At abs_dev = 1.5 * threshold -> 0.95
    # Capped at 1.0
    
    if abs_dev >= threshold * 2.0:
        return 1.0
        
    # Scale such that abs_dev / threshold maps to ~0.8 using sigmoid or ratio
    ratio = abs_dev / threshold
    if ratio < 1.0:
        # Linear or smooth curve up to threshold: 0 to 0.8
        score = 0.8 * (ratio ** 1.1)
    else:
        # Saturation from 0.8 to 1.0
        overflow = ratio - 1.0
        score = 0.8 + 0.2 * (1.0 - math.exp(-2.0 * overflow))
        
    return max(0.0, min(1.0, float(score)))

def determine_direction(current: Optional[float], baseline: Optional[float], eps: float = 1e-4) -> str:
    """
    Determines the directional change between current and baseline.
    Returns: INCREASE, DECREASE, STABLE, or UNKNOWN
    """
    if current is None or baseline is None:
        return "UNKNOWN"
        
    try:
        curr_f = float(current)
        base_f = float(baseline)
    except (ValueError, TypeError):
        return "UNKNOWN"
        
    if math.isnan(curr_f) or math.isnan(base_f) or math.isinf(curr_f) or math.isinf(base_f):
        return "UNKNOWN"
        
    diff = curr_f - base_f
    rel_diff = abs(diff) / max(abs(base_f), 1e-3)
    
    if rel_diff < 0.05: # Less than 5% relative change
        return "STABLE"
    elif diff > 0:
        return "INCREASE"
    else:
        return "DECREASE"
