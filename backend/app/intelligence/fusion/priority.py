from typing import List, Tuple, Optional, Dict, Any
from app.intelligence.fusion.config import PRIORITY_WEIGHTS, SEVERITY_THRESHOLDS, PRIORITY_THRESHOLDS
from app.intelligence.fusion.evidence import IndicatorEvidenceResult

def calculate_severity(combined_evidence: float, max_robust_dev: float = 0.0) -> Tuple[str, float]:
    """
    Calculates analytical anomaly severity category and normalized severity score (0.0 to 1.0).
    
    Categories: LOW, MODERATE-LOW, MODERATE, HIGH, VERY HIGH
    """
    # Normalized severity combines combined evidence and max robust deviation
    dev_norm = min(1.0, max_robust_dev / 6.0) if max_robust_dev > 0 else 0.0
    severity_norm = max(combined_evidence, dev_norm)
    severity_norm = max(0.0, min(1.0, float(severity_norm)))

    category = "LOW"
    for threshold, cat in SEVERITY_THRESHOLDS:
        if severity_norm <= threshold:
            category = cat
            break
        elif threshold == 1.00:
            category = cat

    return category, round(severity_norm, 4)

def calculate_priority_score(
    combined_evidence: float,
    severity_normalized: float,
    confidence_normalized: float,
    model_support_factor: float
) -> Tuple[float, str]:
    """
    Computes investigation_priority_score (0-100) and priority_band.
    
    Formula:
    priority_norm = 0.45 * combined_evidence + 0.20 * severity_norm + 0.20 * conf_norm + 0.15 * model_support
    investigation_priority_score = round(priority_norm * 100)
    """
    w_e = PRIORITY_WEIGHTS["evidence"]
    w_s = PRIORITY_WEIGHTS["severity"]
    w_c = PRIORITY_WEIGHTS["confidence"]
    w_m = PRIORITY_WEIGHTS["model_support"]

    prio_norm = (
        w_e * combined_evidence +
        w_s * severity_normalized +
        w_c * confidence_normalized +
        w_m * model_support_factor
    )

    prio_norm = max(0.0, min(1.0, float(prio_norm)))
    prio_score = round(prio_norm * 100.0, 1)

    # Determine priority band
    band = "LOW PRIORITY"
    for threshold, b_name in PRIORITY_THRESHOLDS:
        if prio_score <= threshold:
            band = b_name
            break
        elif threshold == 100.0:
            band = b_name

    return prio_score, band

def identify_drivers(
    evidence_list: List[IndicatorEvidenceResult]
) -> Tuple[Optional[str], List[str]]:
    """
    Identifies primary driver and supporting indicators sorted by weighted contribution DESC.
    """
    available = [e for e in evidence_list if e.available]
    if not available:
        return None, []

    sorted_ev = sorted(available, key=lambda x: x.weighted_contribution, reverse=True)

    primary_driver = sorted_ev[0].indicator_name if sorted_ev[0].weighted_contribution > 0 else sorted_ev[0].indicator_name
    supporting_indicators = [e.indicator_name for e in sorted_ev[1:]]

    return primary_driver, supporting_indicators
