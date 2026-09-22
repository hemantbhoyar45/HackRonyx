"""
Pure statistical functions for baseline computation.
All functions operate on plain Python lists/numpy arrays — fully unit-testable.
"""
import math
from typing import List, Optional, Dict, Any


def _sorted(values: List[float]) -> List[float]:
    return sorted(v for v in values if v is not None and not math.isnan(v) and not math.isinf(v))


def calc_median(values: List[float]) -> Optional[float]:
    s = _sorted(values)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0


def calc_mean(values: List[float]) -> Optional[float]:
    s = _sorted(values)
    if not s:
        return None
    return sum(s) / len(s)


def calc_std(values: List[float]) -> Optional[float]:
    s = _sorted(values)
    n = len(s)
    if n < 2:
        return 0.0
    mean = sum(s) / n
    variance = sum((x - mean) ** 2 for x in s) / (n - 1)
    return math.sqrt(variance)


def calc_mad(values: List[float]) -> Optional[float]:
    """Median Absolute Deviation — robust variability measure."""
    s = _sorted(values)
    if not s:
        return None
    med = calc_median(s)
    if med is None:
        return None
    deviations = [abs(v - med) for v in s]
    return calc_median(deviations)


def calc_percentile(values: List[float], p: float) -> Optional[float]:
    """Calculate percentile p (0–100) using linear interpolation."""
    s = _sorted(values)
    n = len(s)
    if n == 0:
        return None
    if n == 1:
        return s[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return s[lo]
    frac = idx - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def calc_baseline_stats(values: List[float], min_obs: int = 3) -> Dict[str, Any]:
    """
    Compute all baseline statistics from a list of observations.
    Returns a dict containing median, mean, std, mad, percentiles, count, and status.
    """
    clean = _sorted(values)
    n = len(clean)

    if n < min_obs:
        return {
            "observation_count": n,
            "median": None,
            "mean": None,
            "std": None,
            "mad": None,
            "p10": None,
            "p25": None,
            "p75": None,
            "p90": None,
            "baseline_status": "insufficient_history",
        }

    return {
        "observation_count": n,
        "median": calc_median(clean),
        "mean": calc_mean(clean),
        "std": calc_std(clean),
        "mad": calc_mad(clean),
        "p10": calc_percentile(clean, 10),
        "p25": calc_percentile(clean, 25),
        "p75": calc_percentile(clean, 75),
        "p90": calc_percentile(clean, 90),
        "baseline_status": "available",
    }
