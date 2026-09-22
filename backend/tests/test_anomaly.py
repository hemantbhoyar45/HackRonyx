import pytest
from app.intelligence.anomaly.models import AnomalyFeature, MLAnomalyResult
from app.intelligence.anomaly.features import compute_robust_deviation, extract_features
from app.intelligence.anomaly.statistical import check_statistical_anomaly
from app.intelligence.anomaly.ml import run_isolation_forest, _build_feature_vector
from app.intelligence.anomaly.orchestrator import combine_status, calculate_anomaly_score, analyze_zone_anomaly

class TestFeatures:
    def test_compute_robust_deviation(self):
        # Normal
        assert round(compute_robust_deviation(10.0, 5.0, 2.0), 2) == 2.5
        
        # Zero MAD -> uses epsilon
        dev = compute_robust_deviation(10.0, 5.0, 0.0, epsilon=1e-6)
        assert dev == 100.0 # capped
        
        # NaN
        assert compute_robust_deviation(float('nan'), 5.0, 2.0) == 0.0

    def test_extract_features(self):
        current_stats = {"mean": 0.5, "valid_pixel_percentage": 90.0}
        baseline_stats = {"median": 0.4, "mad": 0.05}
        
        feat = extract_features("ndti", current_stats, baseline_stats)
        assert feat.indicator_name == "ndti"
        assert feat.current_value == 0.5
        assert feat.baseline_median == 0.4
        assert round(feat.absolute_deviation, 2) == 0.1
        assert round(feat.relative_deviation, 2) == 0.25
        assert round(feat.robust_deviation, 2) == 2.0
        assert feat.valid_percentage == 90.0
        
    def test_extract_features_no_baseline(self):
        feat = extract_features("ndti", {"mean": 0.5}, None)
        assert feat.robust_deviation == 0.0

class TestStatistical:
    def test_statistical_anomaly(self):
        features = {
            "ndti": AnomalyFeature("ndti", 0.5, 0.4, 0.1, 0.25, 2.5),
            "fai": AnomalyFeature("fai", 0.5, 0.4, 0.1, 0.25, 3.5), # breaches 3.0
        }
        assert check_statistical_anomaly(features, 3.0) == True
        assert check_statistical_anomaly(features, 4.0) == False

class TestIsolationForest:
    def test_insufficient_data(self):
        historical = [{"indicators": {"ndti": {"mean": 0.1}}}] * 10
        current = {"ndti": AnomalyFeature("ndti", 0.5, 0.4, 0.1, 0.25, 2.5)}
        
        res = run_isolation_forest(historical, current)
        assert res.status == "insufficient_data"
        
    def test_sufficient_data_and_prediction(self):
        # 40 normal historical samples
        historical = [{"indicators": {"ndti": {"mean": 0.1}}}] * 40
        # anomalous current
        current = {"ndti": AnomalyFeature("ndti", 0.9, 0.1, 0.8, 8.0, 10.0)}
        
        res = run_isolation_forest(historical, current)
        assert res.status == "available"
        assert res.prediction in [-1, 1]

class TestOrchestrator:
    def test_combine_status(self):
        # Stats anomaly, no ML data
        assert combine_status(True, MLAnomalyResult("iso", "insufficient_data")) == "POTENTIAL_ANOMALY"
        assert combine_status(False, MLAnomalyResult("iso", "insufficient_data")) == "NO_ANOMALY_SIGNAL"
        
        # Both anomaly
        assert combine_status(True, MLAnomalyResult("iso", "available", prediction=-1)) == "POTENTIAL_ANOMALY"
        
        # Mixed
        assert combine_status(True, MLAnomalyResult("iso", "available", prediction=1)) == "MIXED_EVIDENCE"
        assert combine_status(False, MLAnomalyResult("iso", "available", prediction=-1)) == "MIXED_EVIDENCE"
        
        # Neither
        assert combine_status(False, MLAnomalyResult("iso", "available", prediction=1)) == "NO_ANOMALY_SIGNAL"

    def test_analyze_zone_quality_gate(self):
        res = analyze_zone_anomaly(
            "wb1", "zone1", "s1", "2024-01-01",
            current_indicators={"ndti": {"mean": 0.5, "valid_pixel_percentage": 10.0}},
            baseline_indicators={"ndti": {"median": 0.4, "mad": 0.1}},
            historical_observations=[]
        )
        assert res.combined_status == "LOW_QUALITY_OBSERVATION"
