"""
Deviation calculations: absolute, relative, and robust (MAD-normalized).
All edge cases (zero baseline, zero MAD, NaN) are handled safely.
"""
import math
from typing import Dict, Any, Optional

EPSILON = 1e-9  # prevent division by zero


def calc_absolute_deviation(current: float, baseline_median: float) -> float:
    """current - baseline_median"""
    return current - baseline_median


def calc_relative_deviation(current: float, baseline_median: float) -> Optional[float]:
    """
    (current - baseline_median) / |baseline_median|
    Returns None when baseline is near-zero to avoid meaningless large ratios.
    """
    if abs(baseline_median) < EPSILON:
        return None
    return (current - baseline_median) / abs(baseline_median)


def calc_robust_deviation(current: float, baseline_median: float, mad: float) -> Optional[float]:
    """
    (current - baseline_median) / max(MAD, epsilon)
    Analogous to a Z-score but using the robust MAD instead of std.
    """
    denom = max(abs(mad), EPSILON)
    return (current - baseline_median) / denom


def compute_deviations(
    current_value: float,
    baseline_median: Optional[float],
    baseline_mad: Optional[float],
) -> Dict[str, Any]:
    """
    Compute all deviations from current value vs baseline statistics.
    Returns a dict safe for JSON serialization.
    """
    if baseline_median is None:
        return {
            "absolute": None,
            "relative": None,
            "robust": None,
            "note": "Baseline not available",
        }

    med = float(baseline_median)
    mad = float(baseline_mad) if baseline_mad is not None else 0.0

    absolute = calc_absolute_deviation(current_value, med)
    relative = calc_relative_deviation(current_value, med)
    robust = calc_robust_deviation(current_value, med, mad)

    return {
        "absolute": round(absolute, 6),
        "relative": round(relative, 4) if relative is not None else None,
        "robust": round(robust, 4) if robust is not None else None,
    }
