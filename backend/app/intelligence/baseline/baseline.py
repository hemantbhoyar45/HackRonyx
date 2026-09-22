"""
Top-level baseline orchestrator.
Ties together seasonal baseline computation and deviation calculation
to produce the Prompt 08 data contract.
"""
from typing import Dict, Any, List, Optional
from datetime import date

from app.intelligence.baseline.models import HistoricalObservation, IndicatorBaseline
from app.intelligence.baseline.seasonal import compute_monthly_baseline, build_time_series
from app.intelligence.baseline.deviation import compute_deviations
from app.intelligence.baseline import repository

INDICATORS = ["ndti", "ndci", "fai", "suspended_sediment"]


def get_baseline_for_month(
    water_body_id: str,
    zone_id: str,
    indicator: str,
    month: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> IndicatorBaseline:
    """Retrieve stored observations and compute monthly baseline for one indicator."""
    observations = repository.get_observations(
        water_body_id=water_body_id,
        zone_id=zone_id,
        start_date=start_date,
        end_date=end_date,
    )
    return compute_monthly_baseline(
        water_body_id=water_body_id,
        zone_id=zone_id,
        indicator_name=indicator,
        observations=observations,
        target_month=month,
    )


def build_prompt08_contract(
    water_body_id: str,
    zone_id: str,
    current_date: date,
    current_values: Dict[str, float],
    baseline_start: Optional[date] = None,
    baseline_end: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Build the complete Prompt 08 data contract for all indicators in a zone.
    current_values: {indicator_name: current_median_value}
    """
    month = current_date.month
    result: Dict[str, Any] = {
        "water_body_id": water_body_id,
        "zone_id": zone_id,
        "current_date": current_date.isoformat(),
        "baseline_month": month,
        "indicators": {}
    }

    for indicator in INDICATORS:
        baseline = get_baseline_for_month(
            water_body_id=water_body_id,
            zone_id=zone_id,
            indicator=indicator,
            month=month,
            start_date=baseline_start,
            end_date=baseline_end,
        )

        current_val = current_values.get(indicator)
        if current_val is None:
            continue

        deviations = compute_deviations(
            current_value=current_val,
            baseline_median=baseline.median if baseline.baseline_status == "available" else None,
            baseline_mad=baseline.mad if baseline.baseline_status == "available" else None,
        )

        result["indicators"][indicator] = {
            "current_value": current_val,
            "baseline": {
                "month": baseline.month,
                "observation_count": baseline.observation_count,
                "median": baseline.median if baseline.baseline_status == "available" else None,
                "mean": baseline.mean if baseline.baseline_status == "available" else None,
                "std": baseline.std if baseline.baseline_status == "available" else None,
                "mad": baseline.mad if baseline.baseline_status == "available" else None,
                "p10": baseline.p10 if baseline.baseline_status == "available" else None,
                "p25": baseline.p25 if baseline.baseline_status == "available" else None,
                "p75": baseline.p75 if baseline.baseline_status == "available" else None,
                "p90": baseline.p90 if baseline.baseline_status == "available" else None,
                "status": baseline.baseline_status,
            },
            "deviation": deviations,
        }

    return result


def get_time_series(
    water_body_id: str,
    zone_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Return time-series data for charting.
    """
    observations = repository.get_observations(
        water_body_id=water_body_id,
        zone_id=zone_id,
        start_date=start_date,
        end_date=end_date,
    )
    series = build_time_series(observations)
    return {
        "water_body_id": water_body_id,
        "zone_id": zone_id,
        "observation_count": len(observations),
        "series": series,
    }
