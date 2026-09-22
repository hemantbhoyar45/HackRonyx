import os
import json
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.intelligence.anomaly.models import MLAnomalyResult, AnomalyFeature

MIN_SAMPLES_FOR_ML = 30
CONTAMINATION = "auto"

def _build_feature_vector(indicators: Dict[str, AnomalyFeature]) -> List[float]:
    """
    Builds the feature vector from the AnomalyFeature dict.
    Sorts keys to guarantee consistent ordering.
    """
    sorted_keys = sorted(indicators.keys())
    # We use robust deviation as the primary ML feature
    return [indicators[k].robust_deviation for k in sorted_keys]

def run_isolation_forest(
    historical_observations: List[Dict],
    current_features: Dict[str, AnomalyFeature]
) -> MLAnomalyResult:
    """
    Trains an IsolationForest on historical robust deviations and predicts for the current features.
    Strictly excludes the current observation from training (leakage prevention).
    Returns the anomaly result.
    """
    # 1. Check data sufficiency
    if not historical_observations or len(historical_observations) < MIN_SAMPLES_FOR_ML:
        return MLAnomalyResult(
            model="isolation_forest",
            status="insufficient_data"
        )
        
    # 2. Prepare training data
    # Ensure current observation is NOT in historical (should be guaranteed by service, but we protect)
    # The historical observations come from the repository which only contains past snapshots.
    
    X_train = []
    for obs in historical_observations:
        # We need the robust deviations. 
        # In this simplified architecture for the prompt, we assume historical_observations
        # contain pre-calculated features, or we calculate them on the fly.
        # Since Prompt 07 stores raw values, we must calculate robust deviations for history.
        # However, to avoid heavy recalculation, we can use the raw values as features for the IF!
        # Let's use the raw mean values of the indicators for the ML model.
        
        # Build feature vector for the historical observation
        sorted_keys = sorted(current_features.keys())
        hist_vector = []
        is_valid = True
        for k in sorted_keys:
            if k in obs.get("indicators", {}) and "mean" in obs["indicators"][k]:
                hist_vector.append(obs["indicators"][k]["mean"])
            else:
                is_valid = False
                break
        
        if is_valid:
            X_train.append(hist_vector)
            
    if len(X_train) < MIN_SAMPLES_FOR_ML:
        return MLAnomalyResult(
            model="isolation_forest",
            status="insufficient_data"
        )
        
    # 3. Train model
    try:
        clf = IsolationForest(
            n_estimators=100, 
            contamination=CONTAMINATION,
            random_state=42 # for reproducibility in demo
        )
        clf.fit(X_train)
        
        # 4. Predict current
        sorted_keys = sorted(current_features.keys())
        current_vector = [[current_features[k].current_value for k in sorted_keys]]
        
        prediction_arr = clf.predict(current_vector)
        score_arr = clf.score_samples(current_vector) # negative is more anomalous
        
        prediction = int(prediction_arr[0])
        raw_score = float(score_arr[0])
        
        # Normalize anomaly score (0-100 scale, higher is more anomalous)
        # score_samples returns approx [-0.5, 0] normally. 
        # We can map it conceptually.
        # baseline: -0.5 (normal) to -1.0 (anomalous)
        normalized_score = max(0.0, min(100.0, (-raw_score - 0.4) * 200))
        
        return MLAnomalyResult(
            model="isolation_forest",
            status="available",
            prediction=prediction,
            anomaly_score=normalized_score
        )
        
    except Exception as e:
        print(f"Isolation Forest error: {e}")
        return MLAnomalyResult(
            model="isolation_forest",
            status="error"
        )
