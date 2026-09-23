import pytest
import math
from app.intelligence.fusion.config import (
    INDICATOR_WEIGHTS, PRIORITY_WEIGHTS, CONFIDENCE_WEIGHTS, validate_config
)
from app.intelligence.fusion.normalization import normalize_robust_deviation, determine_direction
from app.intelligence.fusion.evidence import compute_indicator_evidences
from app.intelligence.fusion.agreement import calculate_indicator_agreement
from app.intelligence.fusion.confidence import (
    calculate_quality_factor, calculate_historical_support, calculate_model_support, calculate_confidence_score
)
from app.intelligence.fusion.priority import calculate_severity, calculate_priority_score, identify_drivers
from app.intelligence.fusion.service import MultiIndicatorFusionService

def test_config_validation():
    # Verify default config validates without throwing error
    validate_config()
    assert sum(INDICATOR_WEIGHTS.values()) == 1.0
    assert sum(PRIORITY_WEIGHTS.values()) == 1.0
    assert sum(CONFIDENCE_WEIGHTS.values()) == 1.0

def test_normalization():
    # 0 dev -> ~0.0
    assert normalize_robust_deviation(0.0) == 0.0
    # Threshold dev 3.0 -> ~0.8
    thresh_ev = normalize_robust_deviation(3.0, threshold=3.0)
    assert 0.75 <= thresh_ev <= 0.85
    # Above threshold 6.0 -> 1.0 (capped)
    assert normalize_robust_deviation(6.0, threshold=3.0) == 1.0
    # Negative robust dev handled safely (abs value)
    assert normalize_robust_deviation(-3.0, threshold=3.0) == thresh_ev
    # NaN / Inf / None -> 0.0
    assert normalize_robust_deviation(float('nan')) == 0.0
    assert normalize_robust_deviation(float('inf')) == 0.0
    assert normalize_robust_deviation(None) == 0.0

def test_determine_direction():
    assert determine_direction(0.42, 0.31) == "INCREASE"
    assert determine_direction(0.20, 0.35) == "DECREASE"
    assert determine_direction(0.30, 0.301) == "STABLE"
    assert determine_direction(None, 0.31) == "UNKNOWN"

def test_weighted_fusion():
    indicators_data = {
        "ndti": {"current_value": 0.42, "baseline_median": 0.31, "robust_deviation": 3.4},
        "suspended_sediment": {"current_value": 0.25, "baseline_median": 0.15, "robust_deviation": 2.8},
        "ndci": {"current_value": 0.12, "baseline_median": 0.10, "robust_deviation": 1.2},
        "fai": {"current_value": 0.05, "baseline_median": 0.04, "robust_deviation": 0.5}
    }
    evidences, combined_ev, completeness = compute_indicator_evidences(indicators_data)

    assert len(evidences) == 4
    assert completeness == 1.0
    assert 0.0 <= combined_ev <= 1.0
    
    # Missing 2 indicators test
    partial_data = {
        "ndti": {"current_value": 0.42, "baseline_median": 0.31, "robust_deviation": 3.4},
        "ndci": {"current_value": 0.12, "baseline_median": 0.10, "robust_deviation": 1.2}
    }
    _, partial_ev, partial_completeness = compute_indicator_evidences(partial_data)
    assert partial_completeness == 0.5
    assert partial_ev < combined_ev

def test_agreement():
    indicators_data = {
        "ndti": {"current_value": 0.42, "baseline_median": 0.31, "robust_deviation": 3.4},
        "suspended_sediment": {"current_value": 0.25, "baseline_median": 0.15, "robust_deviation": 3.0},
        "ndci": {"current_value": 0.18, "baseline_median": 0.10, "robust_deviation": 2.5},
        "fai": {"current_value": 0.08, "baseline_median": 0.04, "robust_deviation": 2.2}
    }
    evidences, _, _ = compute_indicator_evidences(indicators_data)
    agr_score = calculate_indicator_agreement(evidences)
    assert agr_score >= 0.70 # Strong multi-indicator agreement

def test_confidence_and_quality():
    q_high = calculate_quality_factor({"valid_percentage": 95.0})
    assert q_high > 0.8

    q_low = calculate_quality_factor({"valid_percentage": 30.0})
    assert q_low <= 0.35

    h_zero = calculate_historical_support(0)
    assert h_zero == 0.0

    h_strong = calculate_historical_support(10)
    assert h_strong == 1.0

    # Model support when ML unavailable
    m_factor, m_score = calculate_model_support(True, {"status": "insufficient_data"})
    assert m_score is None
    assert m_factor == 0.80 # Not penalized

    conf_norm, conf_score = calculate_confidence_score(q_high, 1.0, h_strong, m_factor)
    assert 0.0 <= conf_norm <= 1.0
    assert 0.0 <= conf_score <= 100.0

def test_priority_score_and_severity():
    cat, sev_norm = calculate_severity(0.81, max_robust_dev=3.4)
    assert cat in ["HIGH", "VERY HIGH"]

    prio_score, band = calculate_priority_score(
        combined_evidence=0.81,
        severity_normalized=0.85,
        confidence_normalized=0.87,
        model_support_factor=1.0
    )
    assert 75.0 <= prio_score <= 100.0
    assert band == "VERY HIGH PRIORITY"

def test_multi_zone_fusion_service():
    zone1_data = {
        "zone_id": "Zone-A",
        "combined_status": "POTENTIAL_ANOMALY",
        "statistical_anomaly": True,
        "indicators": {
            "ndti": {"current_value": 0.50, "baseline_median": 0.20, "robust_deviation": 4.5},
            "suspended_sediment": {"current_value": 0.40, "baseline_median": 0.15, "robust_deviation": 4.0},
            "ndci": {"current_value": 0.25, "baseline_median": 0.10, "robust_deviation": 3.2},
            "fai": {"current_value": 0.10, "baseline_median": 0.03, "robust_deviation": 3.0}
        },
        "quality": {"valid_percentage": 92.0}
    }

    zone2_data = {
        "zone_id": "Zone-B",
        "combined_status": "NO_ANOMALY_SIGNAL",
        "statistical_anomaly": False,
        "indicators": {
            "ndti": {"current_value": 0.21, "baseline_median": 0.20, "robust_deviation": 0.2},
            "suspended_sediment": {"current_value": 0.16, "baseline_median": 0.15, "robust_deviation": 0.1}
        },
        "quality": {"valid_percentage": 88.0}
    }

    res1 = MultiIndicatorFusionService.process_zone_anomaly("reservoir-1", "Zone-A", "scene-1", "2026-09-22", zone1_data)
    res2 = MultiIndicatorFusionService.process_zone_anomaly("reservoir-1", "Zone-B", "scene-1", "2026-09-22", zone2_data)

    assert res1["investigation_priority_score"] > res2["investigation_priority_score"]
    assert res1["priority_band"] in ["HIGH PRIORITY", "VERY HIGH PRIORITY"]
    assert res2["priority_band"] == "LOW PRIORITY"
    assert res1["primary_driver"] == "ndti"
