from typing import Dict, Any, Tuple, Optional
from app.intelligence.fusion.config import CONFIDENCE_WEIGHTS

def calculate_quality_factor(quality_info: Optional[Dict[str, Any]]) -> float:
    """
    Calculates observation quality_factor (0.0 to 1.0).
    """
    if not quality_info:
        return 0.7 # Moderate default

    # Check explicit valid_percentage or valid_pixel_percentage
    valid_perc = (
        quality_info.get("valid_percentage") or
        quality_info.get("valid_pixel_percentage") or
        quality_info.get("valid_pixels")
    )
    
    if valid_perc is not None:
        try:
            val = float(valid_perc)
            if val < 50.0:
                return 0.35
            elif val < 80.0:
                return 0.70
            else:
                return 0.95
        except (ValueError, TypeError):
            pass

    status = str(quality_info.get("status", "")).lower()
    if "poor" in status or "low" in status:
        return 0.35
    elif "moderate" in status:
        return 0.70
    elif "good" in status or "high" in status:
        return 0.95

    return 0.75

def calculate_historical_support(observation_count: Optional[int]) -> float:
    """
    Calculates historical support factor (0.0 to 1.0) based on baseline observation count.
    """
    if observation_count is None:
        # Default moderate if unspecified
        return 0.6

    try:
        count = int(observation_count)
    except (ValueError, TypeError):
        return 0.6

    if count <= 0:
        return 0.0
    elif count <= 2:
        return 0.30
    elif count <= 5:
        return 0.65
    else:
        return 1.00

def calculate_model_support(
    statistical_anomaly: bool,
    ml_data: Optional[Dict[str, Any]]
) -> Tuple[float, Optional[float]]:
    """
    Calculates model_support_factor (0.0 to 1.0) and model_agreement_score (1.0, 0.0, or None).
    
    IMPORTANT: If ML model output is unavailable (e.g. insufficient history),
    model_agreement_score is None, and model_support_factor defaults to 0.80 so as not to penalize.
    """
    if not ml_data or not isinstance(ml_data, dict):
        return 0.80, None

    status = ml_data.get("status", "unavailable")
    if status in ["insufficient_data", "unavailable", "skipped_due_to_quality", "skipped"]:
        return 0.80, None

    prediction = ml_data.get("prediction")
    if prediction is None:
        return 0.80, None

    ml_anomaly = (prediction == -1)

    if statistical_anomaly == ml_anomaly:
        # Strong agreement
        return 1.00, 1.0
    else:
        # Mixed evidence between statistical MAD and Isolation Forest
        return 0.60, 0.0

def calculate_confidence_score(
    quality_factor: float,
    indicator_completeness: float,
    historical_support: float,
    model_support_factor: float
) -> Tuple[float, float]:
    """
    Computes confidence_normalized (0.0 to 1.0) and confidence score (0 to 100).
    """
    w_q = CONFIDENCE_WEIGHTS["quality"]
    w_c = CONFIDENCE_WEIGHTS["completeness"]
    w_h = CONFIDENCE_WEIGHTS["historical"]
    w_m = CONFIDENCE_WEIGHTS["model"]

    confidence_norm = (
        w_q * quality_factor +
        w_c * indicator_completeness +
        w_h * historical_support +
        w_m * model_support_factor
    )

    confidence_norm = max(0.0, min(1.0, float(confidence_norm)))
    confidence_score = round(confidence_norm * 100.0, 1)

    return confidence_norm, confidence_score
