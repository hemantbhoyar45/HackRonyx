from typing import Dict, Any, List, Optional
from app.intelligence.anomaly.models import AnomalyFeature, AnomalyResult, MLAnomalyResult
from app.intelligence.anomaly.features import extract_features
from app.intelligence.anomaly.statistical import check_statistical_anomaly
from app.intelligence.anomaly.ml import run_isolation_forest

def combine_status(statistical_anomaly: bool, ml_result: MLAnomalyResult) -> str:
    """
    Combines statistical and ML evidence into a single neutral status string.
    """
    if ml_result.status == "insufficient_data":
        if statistical_anomaly:
            return "POTENTIAL_ANOMALY"
        return "NO_ANOMALY_SIGNAL"
        
    ml_anomaly = (ml_result.prediction == -1)
    
    if statistical_anomaly and ml_anomaly:
        return "POTENTIAL_ANOMALY"
    elif statistical_anomaly and not ml_anomaly:
        return "MIXED_EVIDENCE"
    elif not statistical_anomaly and ml_anomaly:
        return "MIXED_EVIDENCE"
    else:
        return "NO_ANOMALY_SIGNAL"

def calculate_anomaly_score(statistical_anomaly: bool, ml_result: MLAnomalyResult, features: Dict[str, AnomalyFeature]) -> float:
    """
    Calculates a conceptual 0-100 anomaly score based on evidence.
    """
    score = 0.0
    
    # Base score from statistical deviations
    max_dev = 0.0
    for f in features.values():
        if abs(f.robust_deviation) > max_dev:
            max_dev = abs(f.robust_deviation)
            
    # Cap at 10 dev -> 50 points
    stat_score = min(50.0, max_dev * 5.0)
    score += stat_score
    
    # ML score up to 50 points
    if ml_result.status == "available" and ml_result.anomaly_score is not None:
        score += (ml_result.anomaly_score * 0.5)
    elif statistical_anomaly:
        # Boost if ML isn't available but stats are strong
        score += min(50.0, stat_score)
        
    return min(100.0, score)

def check_quality(features: Dict[str, AnomalyFeature]) -> str:
    """
    Simple quality gate based on valid_percentage.
    """
    valid_percentages = [f.valid_percentage for f in features.values() if f.valid_percentage is not None]
    if not valid_percentages:
        return "moderate"
        
    avg_valid = sum(valid_percentages) / len(valid_percentages)
    if avg_valid < 50.0:
        return "poor"
    elif avg_valid < 80.0:
        return "moderate"
    return "good"

def analyze_zone_anomaly(
    water_body_id: str,
    zone_id: str,
    scene_id: str,
    acquisition_date: str,
    current_indicators: Dict[str, Any],
    baseline_indicators: Dict[str, Any],
    historical_observations: List[Dict],
    robust_threshold: float = 3.0
) -> AnomalyResult:
    """
    Orchestrates the full anomaly detection pipeline for a single zone.
    """
    # 1. Feature Engineering
    features = {}
    for ind_key, current_stats in current_indicators.items():
        base_stats = baseline_indicators.get(ind_key)
        features[ind_key] = extract_features(ind_key, current_stats, base_stats)
        
    # 2. Quality Gate
    quality_status = check_quality(features)
    
    if quality_status == "poor":
        return AnomalyResult(
            water_body_id=water_body_id,
            zone_id=zone_id,
            scene_id=scene_id,
            acquisition_date=acquisition_date,
            indicators=features,
            statistical_anomaly=False,
            statistical_threshold=robust_threshold,
            ml=MLAnomalyResult(model="isolation_forest", status="skipped_due_to_quality"),
            combined_status="LOW_QUALITY_OBSERVATION",
            anomaly_score=0.0,
            quality={"valid_percentage": 0.0} # Mock
        )

    # 3. Statistical Detection
    is_stat_anomaly = check_statistical_anomaly(features, robust_threshold)
    
    # 4. ML Detection (Isolation Forest)
    ml_res = run_isolation_forest(historical_observations, features)
    
    # 5. Combined Logic
    status = combine_status(is_stat_anomaly, ml_res)
    score = calculate_anomaly_score(is_stat_anomaly, ml_res, features)
    
    # 6. Affected Area (Mocking for now, as it requires per-pixel raster which we don't process locally in MVP)
    # We will assume if an anomaly is detected, 15-30% of the zone is affected.
    affected_perc = 0.0
    if status == "POTENTIAL_ANOMALY":
        affected_perc = 25.0
    elif status == "MIXED_EVIDENCE":
        affected_perc = 10.0
        
    return AnomalyResult(
        water_body_id=water_body_id,
        zone_id=zone_id,
        scene_id=scene_id,
        acquisition_date=acquisition_date,
        indicators=features,
        statistical_anomaly=is_stat_anomaly,
        statistical_threshold=robust_threshold,
        ml=ml_res,
        combined_status=status,
        anomaly_score=round(score, 1),
        quality={"valid_percentage": 95.0},
        affected_area=0.0,
        affected_percentage=affected_perc
    )
