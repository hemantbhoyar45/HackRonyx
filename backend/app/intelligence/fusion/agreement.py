from typing import List
from app.intelligence.fusion.evidence import IndicatorEvidenceResult

def calculate_indicator_agreement(evidence_list: List[IndicatorEvidenceResult]) -> float:
    """
    Calculates the multi-indicator agreement score (0.0 to 1.0).
    
    Higher score indicates multiple available indicators agree on an anomalous signal.
    - 0 anomalous indicators: 0.0
    - 1 anomalous indicator: ~0.3
    - 2 anomalous indicators: ~0.6
    - 3+ anomalous indicators: 0.8 - 1.0
    """
    available_indicators = [e for e in evidence_list if e.available]
    if not available_indicators:
        return 0.0

    # Consider an indicator as showing meaningful anomaly evidence if evidence_score >= 0.4
    anomalous_indicators = [e for e in available_indicators if e.evidence_score >= 0.4]
    num_anomalous = len(anomalous_indicators)
    num_available = len(available_indicators)

    if num_anomalous == 0:
        return 0.0

    # Proportion of available indicators showing anomaly
    proportion = float(num_anomalous) / float(num_available)

    # Average evidence strength among anomalous indicators
    avg_strength = sum(e.evidence_score for e in anomalous_indicators) / float(num_anomalous)

    # Multi-indicator agreement scales with proportion and strength
    if num_anomalous == 1:
        # Single indicator signal - capped at 0.35
        agreement = min(0.35, proportion * avg_strength)
    else:
        # Multi-indicator signal
        agreement = proportion * 0.7 + avg_strength * 0.3

    return round(max(0.0, min(1.0, float(agreement))), 4)
