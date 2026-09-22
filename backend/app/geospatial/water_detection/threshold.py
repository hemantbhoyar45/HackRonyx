import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

def calculate_otsu_threshold(histogram: List[Tuple[float, float]]) -> Optional[float]:
    """
    Calculates the Otsu threshold from a given histogram.
    The histogram should be a list of [bin_value, frequency] tuples.
    
    If the histogram is empty or invalid, returns None.
    """
    if not histogram:
        return None
        
    total_pixels = sum(freq for _, freq in histogram)
    if total_pixels == 0:
        return None
        
    sum_total = sum(val * freq for val, freq in histogram)
    
    sum_background = 0.0
    weight_background = 0.0
    weight_foreground = 0.0
    
    max_variance = 0.0
    threshold1 = 0.0
    threshold2 = 0.0
    
    for val, freq in histogram:
        weight_background += freq
        if weight_background == 0:
            continue
            
        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break
            
        sum_background += val * freq
        
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground
        
        # Calculate Between Class Variance
        variance_between = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
        
        if variance_between > max_variance:
            max_variance = variance_between
            threshold1 = val
            threshold2 = val
        elif variance_between == max_variance:
            threshold2 = val
            
    # Return the average of the two thresholds if there is a flat peak
    final_threshold = (threshold1 + threshold2) / 2.0
    
    logger.debug(f"Calculated Otsu threshold: {final_threshold} (variance: {max_variance})")
    
    # Basic sanity check to ensure it's not a completely flat image returning 0 variance
    if max_variance == 0:
        return None
        
    return final_threshold
