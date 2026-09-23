"""
Historical service: orchestrates historical observation retrieval/generation,
indicator computation, repository persistence, and baseline preparation.
"""
import logging
import random
import math
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from app.schemas.baseline import (
    HistoricalRequest, HistoricalResponse, HistoricalObservationSchema,
    TimeSeriesPoint, BaselineRequest, BaselineResponse, BaselineStats,
    BaselineCompareRequest, BaselineCompareResponse, DeviationResult,
)
from app.intelligence.baseline.models import HistoricalObservation, IndicatorStats
from app.intelligence.baseline import repository
from app.intelligence.baseline.seasonal import compute_monthly_baseline, build_time_series
from app.intelligence.baseline.deviation import compute_deviations
from app.geospatial.gee.client import is_gee_ready

logger = logging.getLogger(__name__)

# Realistic seasonal multipliers for monsoon-affected Indian water bodies
# Jan=1.0 (baseline), Jun-Sep = higher turbidity/sediment
_SEASONAL_NDTI  = {1:1.0,2:0.95,3:1.05,4:1.1,5:1.15,6:1.4,7:1.6,8:1.55,9:1.45,10:1.2,11:1.05,12:1.0}
_SEASONAL_NDCI  = {1:1.0,2:1.0, 3:1.1, 4:1.2,5:1.3, 6:1.1,7:0.9, 8:0.95,9:1.0, 10:1.1, 11:1.05,12:1.0}
_SEASONAL_FAI   = {1:1.0,2:1.0, 3:1.05,4:1.2,5:1.3, 6:1.1,7:0.9, 8:0.85,9:1.0, 10:1.1, 11:1.0, 12:1.0}
_SEASONAL_SS    = {1:1.0,2:0.9, 3:1.0, 4:1.1,5:1.2, 6:1.5,7:1.8, 8:1.7, 9:1.5, 10:1.3, 11:1.1, 12:1.0}

# Base values per water body
_BASE_VALUES = {
    "gosikhurd-reservoir":      {"ndti": 0.12, "ndci": 0.07, "fai": 0.012, "suspended_sediment": 0.16},
    "godavari-river-segment":   {"ndti": 0.18, "ndci": 0.06, "fai": 0.010, "suspended_sediment": 0.22},
    "wainganga-river-segment":  {"ndti": 0.15, "ndci": 0.06, "fai": 0.009, "suspended_sediment": 0.19},
    "jaikwadi-reservoir":       {"ndti": 0.13, "ndci": 0.08, "fai": 0.013, "suspended_sediment": 0.17},
}
_DEFAULT_BASE = {"ndti": 0.14, "ndci": 0.07, "fai": 0.011, "suspended_sediment": 0.18}


def _seasonal_value(base: float, seasonal_map: dict, month: int, noise_pct: float = 0.08, seed: int = 0) -> float:
    rng = random.Random(seed)
    raw = base * seasonal_map.get(month, 1.0)
    noise = rng.uniform(-noise_pct, noise_pct) * raw
    return round(max(raw + noise, -0.99), 5)


def _generate_demo_observations(
    water_body_id: str,
    zone_id: str,
    start_date: date,
    end_date: date,
) -> List[HistoricalObservation]:
    """
    Generate deterministic synthetic historical observations.
    Produces ~2 scenes/month with realistic seasonal variation.
    Labeled as demo — never presented as real data.
    """
    base = _BASE_VALUES.get(water_body_id, _DEFAULT_BASE)
    observations = []
    current = start_date.replace(day=1)
    scene_idx = 0

    while current <= end_date:
        month = current.month
        # Two observations per month (1st and 15th)
        for day_offset in [5, 20]:
            obs_date = current.replace(day=min(day_offset, 28))
            if obs_date < start_date or obs_date > end_date:
                continue

            seed = hash(f"{water_body_id}{zone_id}{obs_date.isoformat()}") & 0xFFFF
            rng = random.Random(seed)

            ndti_val = _seasonal_value(base["ndti"], _SEASONAL_NDTI, month, seed=seed)
            ndci_val = _seasonal_value(base["ndci"], _SEASONAL_NDCI, month, seed=seed+1)
            fai_val  = _seasonal_value(base["fai"],  _SEASONAL_FAI,  month, seed=seed+2)
            ss_val   = _seasonal_value(base["suspended_sediment"], _SEASONAL_SS, month, seed=seed+3)

            obs = HistoricalObservation(
                water_body_id=water_body_id,
                zone_id=zone_id,
                scene_id=f"DEMO_S2_{obs_date.strftime('%Y%m%d')}_{scene_idx:04d}",
                acquisition_date=obs_date,
                sensor="Sentinel-2",
                water_area_km2=round(rng.uniform(2.0, 3.5), 3),
                valid_pixel_count=rng.randint(12000, 18000),
                observation_status="valid",
                ndti=IndicatorStats(median=ndti_val, mean=round(ndti_val*1.02,5), std=round(abs(ndti_val)*0.1,5), valid_pixel_count=rng.randint(12000,18000)),
                ndci=IndicatorStats(median=ndci_val, mean=round(ndci_val*1.01,5), std=round(abs(ndci_val)*0.12,5), valid_pixel_count=rng.randint(12000,18000)),
                fai=IndicatorStats(median=fai_val,   mean=round(fai_val*1.03,5),  std=round(abs(fai_val)*0.15,5),  valid_pixel_count=rng.randint(12000,18000)),
                suspended_sediment=IndicatorStats(median=ss_val, mean=round(ss_val*1.02,5), std=round(abs(ss_val)*0.09,5), valid_pixel_count=rng.randint(12000,18000)),
                quality_metadata={"data_source": "demo", "cloud_pct": round(rng.uniform(2,15),1)},
            )
            observations.append(obs)
            scene_idx += 1

        # Advance to next month
        if current.month == 12:
            current = current.replace(year=current.year+1, month=1, day=1)
        else:
            current = current.replace(month=current.month+1, day=1)

    return observations


def run_historical(request: HistoricalRequest) -> HistoricalResponse:
    logger.info(f"Historical analysis: {request.water_body_id} {request.start_date}→{request.end_date}")

    # Always use demo mode for historical since GEE calls for every historical scene would be extremely slow.
    # When GEE is connected and a job queue exists, replace _generate_demo_observations with real pipeline.
    observations = _generate_demo_observations(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # Persist to repository
    for obs in observations:
        repository.save_observation(obs)

    # Build time series
    series_raw = build_time_series(observations)
    time_series: Dict[str, List[TimeSeriesPoint]] = {}
    for ind, points in series_raw.items():
        time_series[ind] = [TimeSeriesPoint(**p) for p in points]

    obs_schemas = [
        HistoricalObservationSchema(
            scene_id=o.scene_id,
            acquisition_date=o.acquisition_date,
            sensor=o.sensor,
            water_area_km2=o.water_area_km2,
            valid_pixel_count=o.valid_pixel_count,
            observation_status=o.observation_status,
            ndti_median=o.ndti.median,
            ndci_median=o.ndci.median,
            fai_median=o.fai.median,
            suspended_sediment_median=o.suspended_sediment.median,
        )
        for o in observations
    ]

    valid_count = sum(1 for o in observations if o.observation_status == "valid")
    rejected = len(observations) - valid_count

    return HistoricalResponse(
        status="success",
        data_source_mode="demo",
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        start_date=request.start_date,
        end_date=request.end_date,
        total_scenes_found=len(observations),
        valid_observations=valid_count,
        rejected_observations=rejected,
        observations=obs_schemas,
        time_series=time_series,
        message="Demo historical data generated. Connect GEE for live satellite observations.",
    )


def run_get_baseline(request: BaselineRequest) -> BaselineResponse:
    observations = repository.get_observations(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # If no stored observations, generate demo data first
    if not observations:
        end = request.end_date or date.today()
        start = request.start_date or date(end.year - 2, end.month, 1)
        demo_obs = _generate_demo_observations(request.water_body_id, request.zone_id, start, end)
        for obs in demo_obs:
            repository.save_observation(obs)
        observations = demo_obs

    baseline = compute_monthly_baseline(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        indicator_name=request.indicator,
        observations=observations,
        target_month=request.month,
    )

    return BaselineResponse(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        indicator=request.indicator,
        baseline=BaselineStats(
            month=baseline.month,
            observation_count=baseline.observation_count,
            median=baseline.median if baseline.baseline_status == "available" else None,
            mean=baseline.mean if baseline.baseline_status == "available" else None,
            std=baseline.std if baseline.baseline_status == "available" else None,
            mad=baseline.mad if baseline.baseline_status == "available" else None,
            p10=baseline.p10 if baseline.baseline_status == "available" else None,
            p25=baseline.p25 if baseline.baseline_status == "available" else None,
            p75=baseline.p75 if baseline.baseline_status == "available" else None,
            p90=baseline.p90 if baseline.baseline_status == "available" else None,
            baseline_status=baseline.baseline_status,
        ),
    )


def run_compare_baseline(request: BaselineCompareRequest) -> BaselineCompareResponse:
    baseline_resp = run_get_baseline(BaselineRequest(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        indicator=request.indicator,
        month=request.current_date.month,
        start_date=request.baseline_start,
        end_date=request.baseline_end,
    ))

    b = baseline_resp.baseline
    deviations = compute_deviations(
        current_value=request.current_value,
        baseline_median=b.median,
        baseline_mad=b.mad,
    )

    return BaselineCompareResponse(
        water_body_id=request.water_body_id,
        zone_id=request.zone_id,
        indicator=request.indicator,
        current_value=request.current_value,
        current_date=request.current_date,
        baseline=b,
        deviation=DeviationResult(**deviations),
    )


class HistoricalService:
    """
    Service wrapper for historical data generation and baseline queries.
    """
    async def get_historical_analysis(self, water_body_id: str, zone_id: str, start_date: str, end_date: str):
        from datetime import datetime
        s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        e_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        req = HistoricalRequest(
            water_body_id=water_body_id,
            zone_id=zone_id,
            start_date=s_date,
            end_date=e_date
        )
        return run_historical(req)

    def _generate_demo_observation(self, water_body_id: str, zone_id: str, date_str: str):
        from datetime import datetime
        obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return _generate_demo_obs(water_body_id, zone_id, obs_date)

