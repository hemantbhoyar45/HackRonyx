"""
Unit tests for Prompt 07 — Historical Baseline & Time-Series.
Run with: pytest tests/test_baseline.py -v
"""
import pytest
from datetime import date

from app.intelligence.baseline.statistics import (
    calc_median, calc_mean, calc_std, calc_mad,
    calc_percentile, calc_baseline_stats,
)
from app.intelligence.baseline.deviation import (
    calc_absolute_deviation, calc_relative_deviation,
    calc_robust_deviation, compute_deviations,
)
from app.intelligence.baseline.models import HistoricalObservation, IndicatorStats
from app.intelligence.baseline.seasonal import (
    group_by_month, compute_monthly_baseline, build_time_series,
)


# ─────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────

class TestStatistics:
    def test_median_odd(self):
        assert calc_median([1, 3, 5]) == 3.0

    def test_median_even(self):
        assert calc_median([1, 2, 3, 4]) == 2.5

    def test_median_empty(self):
        assert calc_median([]) is None

    def test_mean_basic(self):
        assert calc_mean([1, 2, 3, 4, 5]) == 3.0

    def test_std_basic(self):
        std = calc_std([2, 4, 4, 4, 5, 5, 7, 9])
        assert round(std, 2) == 2.14  # sample std (Bessel correction, n-1)

    def test_std_single_element(self):
        assert calc_std([5.0]) == 0.0

    def test_mad_basic(self):
        mad = calc_mad([1, 1, 2, 2, 4, 6, 9])
        assert mad == 1.0  # Median=2, deviations=[1,1,0,0,2,4,7], median=1

    def test_mad_empty(self):
        assert calc_mad([]) is None

    def test_percentile_p25(self):
        p = calc_percentile([1, 2, 3, 4], 25)
        assert p == 1.75

    def test_percentile_p75(self):
        p = calc_percentile([1, 2, 3, 4], 75)
        assert p == 3.25

    def test_percentile_empty(self):
        assert calc_percentile([], 50) is None

    def test_baseline_stats_available(self):
        values = [0.10, 0.12, 0.14, 0.11, 0.13]
        stats = calc_baseline_stats(values, min_obs=3)
        assert stats["baseline_status"] == "available"
        assert stats["observation_count"] == 5
        assert stats["median"] == 0.12
        assert stats["mad"] is not None

    def test_baseline_stats_insufficient(self):
        values = [0.10, 0.12]
        stats = calc_baseline_stats(values, min_obs=3)
        assert stats["baseline_status"] == "insufficient_history"
        assert stats["median"] is None

    def test_baseline_stats_nan_filtered(self):
        import math
        values = [0.10, float("nan"), 0.12, float("inf"), 0.14]
        stats = calc_baseline_stats(values, min_obs=3)
        assert stats["baseline_status"] == "available"
        assert stats["observation_count"] == 3


# ─────────────────────────────────────────────
# Deviation
# ─────────────────────────────────────────────

class TestDeviation:
    def test_absolute(self):
        assert calc_absolute_deviation(0.20, 0.12) == pytest.approx(0.08)

    def test_relative(self):
        r = calc_relative_deviation(0.20, 0.12)
        assert round(r, 4) == pytest.approx(0.6667, abs=1e-3)

    def test_relative_zero_baseline(self):
        assert calc_relative_deviation(0.20, 0.0) is None

    def test_relative_near_zero_baseline(self):
        assert calc_relative_deviation(0.20, 1e-10) is None

    def test_robust(self):
        r = calc_robust_deviation(0.20, 0.12, 0.02)
        assert r == pytest.approx(4.0)

    def test_robust_zero_mad(self):
        # Should use epsilon instead of 0 and return finite value
        r = calc_robust_deviation(0.20, 0.12, 0.0)
        assert r is not None
        assert abs(r) > 1000  # Very large but not inf

    def test_compute_deviations_no_baseline(self):
        result = compute_deviations(0.20, None, None)
        assert result["absolute"] is None
        assert "note" in result

    def test_compute_deviations_full(self):
        result = compute_deviations(0.20, 0.12, 0.02)
        assert result["absolute"] == pytest.approx(0.08)
        assert result["relative"] == pytest.approx(0.6667, abs=1e-3)
        assert result["robust"] == pytest.approx(4.0)


# ─────────────────────────────────────────────
# Seasonal Grouping
# ─────────────────────────────────────────────

def _make_obs(month: int, ndti: float, wb_id: str = "test") -> HistoricalObservation:
    return HistoricalObservation(
        water_body_id=wb_id,
        zone_id="zone-main",
        scene_id=f"S2_{month}_{int(ndti*100)}",
        acquisition_date=date(2024, month, 15),
        ndti=IndicatorStats(median=ndti, mean=ndti, std=0.01, valid_pixel_count=1000),
        ndci=IndicatorStats(median=0.07, mean=0.07, std=0.005, valid_pixel_count=1000),
        fai=IndicatorStats(median=0.01, mean=0.01, std=0.001, valid_pixel_count=1000),
        suspended_sediment=IndicatorStats(median=0.15, mean=0.15, std=0.01, valid_pixel_count=1000),
    )


class TestSeasonal:
    def test_group_by_month(self):
        obs = [_make_obs(1, 0.10), _make_obs(1, 0.11), _make_obs(7, 0.18)]
        groups = group_by_month(obs)
        assert len(groups[1]) == 2
        assert len(groups[7]) == 1
        assert len(groups[3]) == 0

    def test_compute_monthly_baseline_available(self):
        obs = [_make_obs(6, 0.14), _make_obs(6, 0.16), _make_obs(6, 0.15)]
        baseline = compute_monthly_baseline("test", "zone-main", "ndti", obs, 6, min_obs=3)
        assert baseline.baseline_status == "available"
        assert baseline.median == pytest.approx(0.15)
        assert baseline.month == 6

    def test_compute_monthly_baseline_insufficient(self):
        obs = [_make_obs(6, 0.14)]
        baseline = compute_monthly_baseline("test", "zone-main", "ndti", obs, 6, min_obs=3)
        assert baseline.baseline_status == "insufficient_history"

    def test_build_time_series(self):
        obs = [_make_obs(1, 0.10), _make_obs(3, 0.12), _make_obs(7, 0.18)]
        series = build_time_series(obs)
        assert "ndti" in series
        assert len(series["ndti"]) == 3
        # Sorted by date
        dates = [p["date"] for p in series["ndti"]]
        assert dates == sorted(dates)


# ─────────────────────────────────────────────
# Demo Data Generation
# ─────────────────────────────────────────────

class TestDemoGeneration:
    def test_generates_observations(self):
        from app.services.historical_service import _generate_demo_observations
        obs = _generate_demo_observations(
            water_body_id="gosikhurd-reservoir",
            zone_id="zone-main",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 31),
        )
        assert len(obs) > 0
        for o in obs:
            assert o.observation_status == "valid"
            assert o.water_body_id == "gosikhurd-reservoir"
            assert o.zone_id == "zone-main"
            # Dates must be within range
            assert date(2023, 1, 1) <= o.acquisition_date <= date(2023, 3, 31)

    def test_seasonal_monsoon_higher(self):
        """July (monsoon) observations should have higher NDTI and sediment than January."""
        from app.services.historical_service import _generate_demo_observations
        obs = _generate_demo_observations(
            water_body_id="gosikhurd-reservoir",
            zone_id="zone-main",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
        )
        jan = [o.ndti.median for o in obs if o.acquisition_date.month == 1]
        jul = [o.ndti.median for o in obs if o.acquisition_date.month == 7]
        assert jan and jul
        assert sum(jul) / len(jul) > sum(jan) / len(jan), "July NDTI should be > January NDTI"

    def test_deterministic(self):
        """Same inputs produce identical observations."""
        from app.services.historical_service import _generate_demo_observations
        obs1 = _generate_demo_observations("gosikhurd-reservoir", "zone-main", date(2023, 6, 1), date(2023, 6, 30))
        obs2 = _generate_demo_observations("gosikhurd-reservoir", "zone-main", date(2023, 6, 1), date(2023, 6, 30))
        vals1 = [o.ndti.median for o in obs1]
        vals2 = [o.ndti.median for o in obs2]
        assert vals1 == vals2
