"""
Seasonal (month-of-year) grouping and baseline computation.
"""
from typing import List, Dict, Any, Optional
from datetime import date

from app.intelligence.baseline.models import HistoricalObservation, IndicatorBaseline
from app.intelligence.baseline.statistics import calc_baseline_stats

INDICATORS = ["ndti", "ndci", "fai", "suspended_sediment"]
MIN_BASELINE_OBSERVATIONS = 3  # configurable


def group_by_month(observations: List[HistoricalObservation]) -> Dict[int, List[HistoricalObservation]]:
    """Group observations into a dict keyed by month-of-year (1–12)."""
    groups: Dict[int, List[HistoricalObservation]] = {m: [] for m in range(1, 13)}
    for obs in observations:
        groups[obs.acquisition_date.month].append(obs)
    return groups


def compute_monthly_baseline(
    water_body_id: str,
    zone_id: str,
    indicator_name: str,
    observations: List[HistoricalObservation],
    target_month: int,
    min_obs: int = MIN_BASELINE_OBSERVATIONS,
) -> IndicatorBaseline:
    """
    Compute baseline for a specific month-of-year and indicator.
    Uses only observations from the given month.
    """
    monthly_obs = [o for o in observations if o.acquisition_date.month == target_month]
    values = [getattr(o, indicator_name).median for o in monthly_obs if getattr(o, indicator_name).median is not None]

    stats = calc_baseline_stats(values, min_obs=min_obs)

    return IndicatorBaseline(
        water_body_id=water_body_id,
        zone_id=zone_id,
        indicator_name=indicator_name,
        month=target_month,
        observation_count=stats["observation_count"],
        median=stats["median"] or 0.0,
        mean=stats["mean"] or 0.0,
        std=stats["std"] or 0.0,
        mad=stats["mad"] or 0.0,
        p10=stats["p10"] or 0.0,
        p25=stats["p25"] or 0.0,
        p75=stats["p75"] or 0.0,
        p90=stats["p90"] or 0.0,
        baseline_status=stats["baseline_status"],
    )


def compute_all_monthly_baselines(
    water_body_id: str,
    zone_id: str,
    observations: List[HistoricalObservation],
    min_obs: int = MIN_BASELINE_OBSERVATIONS,
) -> Dict[str, Dict[int, IndicatorBaseline]]:
    """
    Compute baselines for ALL indicators and ALL months.
    Returns: {indicator_name: {month: IndicatorBaseline}}
    """
    result: Dict[str, Dict[int, IndicatorBaseline]] = {}
    for indicator in INDICATORS:
        result[indicator] = {}
        for month in range(1, 13):
            result[indicator][month] = compute_monthly_baseline(
                water_body_id=water_body_id,
                zone_id=zone_id,
                indicator_name=indicator,
                observations=observations,
                target_month=month,
                min_obs=min_obs,
            )
    return result


def build_time_series(
    observations: List[HistoricalObservation],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Build a time-series dict keyed by indicator for chart rendering.
    Each point has: date, median, mean, std.
    """
    series: Dict[str, List[Dict[str, Any]]] = {ind: [] for ind in INDICATORS}
    for obs in sorted(observations, key=lambda o: o.acquisition_date):
        for ind in INDICATORS:
            stats = getattr(obs, ind)
            series[ind].append({
                "date": obs.acquisition_date.isoformat(),
                "scene_id": obs.scene_id,
                "median": stats.median,
                "mean": stats.mean,
                "std": stats.std,
                "observation_status": obs.observation_status,
            })
    return series
