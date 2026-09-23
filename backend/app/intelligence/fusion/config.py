from typing import Dict, Any

# Target Indicators to Fuse
TARGET_INDICATORS = ["ndti", "suspended_sediment", "ndci", "fai"]

# Centralized Indicator Weights (must sum to 1.0)
INDICATOR_WEIGHTS: Dict[str, float] = {
    "ndti": 0.30,
    "suspended_sediment": 0.25,
    "ndci": 0.20,
    "fai": 0.25
}

# Robust deviation threshold for evidence scaling
ROBUST_DEVIATION_THRESHOLD: float = 3.0

# Centralized Priority Weights (must sum to 1.0)
PRIORITY_WEIGHTS: Dict[str, float] = {
    "evidence": 0.45,
    "severity": 0.20,
    "confidence": 0.20,
    "model_support": 0.15
}

# Confidence Component Weights (must sum to 1.0)
CONFIDENCE_WEIGHTS: Dict[str, float] = {
    "quality": 0.35,
    "completeness": 0.25,
    "historical": 0.20,
    "model": 0.20
}

# Severity Thresholds (analytical anomaly categories)
# Format: (max_val, category_name)
SEVERITY_THRESHOLDS = [
    (0.24, "LOW"),
    (0.49, "MODERATE-LOW"),
    (0.69, "MODERATE"),
    (0.70, "HIGH"),
    (0.85, "VERY HIGH")
]

# Priority Band Thresholds (0-100 score)
PRIORITY_THRESHOLDS = [
    (24.0, "LOW PRIORITY"),
    (49.0, "MEDIUM PRIORITY"),
    (74.0, "HIGH PRIORITY"),
    (100.0, "VERY HIGH PRIORITY")
]

# Validation function to ensure mathematical consistency
def validate_config() -> None:
    ind_sum = sum(INDICATOR_WEIGHTS.values())
    if abs(ind_sum - 1.0) > 1e-5:
        raise ValueError(f"INDICATOR_WEIGHTS must sum to 1.0, got {ind_sum}")
        
    prio_sum = sum(PRIORITY_WEIGHTS.values())
    if abs(prio_sum - 1.0) > 1e-5:
        raise ValueError(f"PRIORITY_WEIGHTS must sum to 1.0, got {prio_sum}")
        
    conf_sum = sum(CONFIDENCE_WEIGHTS.values())
    if abs(conf_sum - 1.0) > 1e-5:
        raise ValueError(f"CONFIDENCE_WEIGHTS must sum to 1.0, got {conf_sum}")

# Run validation on import
validate_config()
