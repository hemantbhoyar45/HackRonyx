"""
Historical Observation and Baseline data models.
Designed to mirror the PostgreSQL schema for easy migration.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import date


@dataclass
class IndicatorStats:
    """Per-indicator statistics for a single observation."""
    median: float = 0.0
    mean: float = 0.0
    std: float = 0.0
    valid_pixel_count: int = 0


@dataclass
class HistoricalObservation:
    """
    One processed satellite observation for a specific zone.
    Maps to the `historical_observations` PostgreSQL table.
    """
    water_body_id: str
    zone_id: str
    scene_id: str
    acquisition_date: date
    sensor: str = "Sentinel-2"
    water_area_km2: float = 0.0
    valid_pixel_count: int = 0
    observation_status: str = "valid"  # valid | low_quality | rejected

    # Per-indicator stats
    ndti: IndicatorStats = field(default_factory=IndicatorStats)
    ndci: IndicatorStats = field(default_factory=IndicatorStats)
    fai: IndicatorStats = field(default_factory=IndicatorStats)
    suspended_sediment: IndicatorStats = field(default_factory=IndicatorStats)

    quality_metadata: Dict[str, Any] = field(default_factory=dict)

    def month(self) -> int:
        """Return month-of-year (1–12) for seasonal grouping."""
        return self.acquisition_date.month

    def to_dict(self) -> Dict[str, Any]:
        return {
            "water_body_id": self.water_body_id,
            "zone_id": self.zone_id,
            "scene_id": self.scene_id,
            "acquisition_date": self.acquisition_date.isoformat(),
            "sensor": self.sensor,
            "water_area_km2": self.water_area_km2,
            "valid_pixel_count": self.valid_pixel_count,
            "observation_status": self.observation_status,
            "ndti": {"median": self.ndti.median, "mean": self.ndti.mean, "std": self.ndti.std, "valid_pixel_count": self.ndti.valid_pixel_count},
            "ndci": {"median": self.ndci.median, "mean": self.ndci.mean, "std": self.ndci.std, "valid_pixel_count": self.ndci.valid_pixel_count},
            "fai": {"median": self.fai.median, "mean": self.fai.mean, "std": self.fai.std, "valid_pixel_count": self.fai.valid_pixel_count},
            "suspended_sediment": {"median": self.suspended_sediment.median, "mean": self.suspended_sediment.mean, "std": self.suspended_sediment.std, "valid_pixel_count": self.suspended_sediment.valid_pixel_count},
            "quality_metadata": self.quality_metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HistoricalObservation":
        acq_date = d["acquisition_date"]
        if isinstance(acq_date, str):
            acq_date = date.fromisoformat(acq_date)
        obs = cls(
            water_body_id=d["water_body_id"],
            zone_id=d["zone_id"],
            scene_id=d["scene_id"],
            acquisition_date=acq_date,
            sensor=d.get("sensor", "Sentinel-2"),
            water_area_km2=d.get("water_area_km2", 0.0),
            valid_pixel_count=d.get("valid_pixel_count", 0),
            observation_status=d.get("observation_status", "valid"),
            quality_metadata=d.get("quality_metadata", {}),
        )
        for ind in ("ndti", "ndci", "fai", "suspended_sediment"):
            raw = d.get(ind, {})
            setattr(obs, ind, IndicatorStats(
                median=raw.get("median", 0.0),
                mean=raw.get("mean", 0.0),
                std=raw.get("std", 0.0),
                valid_pixel_count=raw.get("valid_pixel_count", 0),
            ))
        return obs


@dataclass
class IndicatorBaseline:
    """
    Computed monthly baseline for one indicator in one zone.
    Maps to the `indicator_baselines` PostgreSQL table.
    """
    water_body_id: str
    zone_id: str
    indicator_name: str
    month: int  # 1–12
    observation_count: int = 0
    median: float = 0.0
    mean: float = 0.0
    std: float = 0.0
    mad: float = 0.0
    p10: float = 0.0
    p25: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    baseline_status: str = "insufficient_history"  # available | insufficient_history
