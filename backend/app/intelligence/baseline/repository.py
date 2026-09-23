"""
In-memory repository for historical observations with JSON file persistence.
Designed for easy migration to PostgreSQL — just swap the store methods.
"""
import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import List, Optional
from threading import Lock

from app.intelligence.baseline.models import HistoricalObservation

logger = logging.getLogger(__name__)

# Storage path — use a data directory inside the backend folder
_DATA_DIR = Path(os.environ.get("BASELINE_DATA_DIR", "data/baseline"))
_LOCK = Lock()

INDICATORS = ["ndti", "ndci", "fai", "suspended_sediment"]


def _store_path(water_body_id: str) -> Path:
    safe = water_body_id.replace("/", "_").replace(" ", "_")
    return _DATA_DIR / f"{safe}.json"


def _load_raw(water_body_id: str) -> List[dict]:
    path = _store_path(water_body_id)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load baseline store for {water_body_id}: {e}")
        return []


def _save_raw(water_body_id: str, records: List[dict]) -> None:
    path = _store_path(water_body_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def save_observation(obs: HistoricalObservation) -> None:
    """Upsert a single observation (keyed by water_body+zone+scene_id)."""
    with _LOCK:
        records = _load_raw(obs.water_body_id)
        # Dedup by scene_id + zone_id
        records = [r for r in records if not (
            r["scene_id"] == obs.scene_id and r["zone_id"] == obs.zone_id
        )]
        records.append(obs.to_dict())
        _save_raw(obs.water_body_id, records)


def get_observations(
    water_body_id: str,
    zone_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status_filter: str = "valid",
) -> List[HistoricalObservation]:
    """Return observations filtered by zone and date range."""
    records = _load_raw(water_body_id)
    results = []
    for r in records:
        obs = HistoricalObservation.from_dict(r)
        if zone_id and obs.zone_id != zone_id:
            continue
        if status_filter and obs.observation_status != status_filter:
            continue
        if start_date and obs.acquisition_date < start_date:
            continue
        if end_date and obs.acquisition_date > end_date:
            continue
        results.append(obs)
    results.sort(key=lambda o: o.acquisition_date)
    return results


def get_by_month(
    water_body_id: str,
    zone_id: str,
    month: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[HistoricalObservation]:
    """Return valid observations for a specific month-of-year."""
    all_obs = get_observations(
        water_body_id=water_body_id,
        zone_id=zone_id,
        start_date=start_date,
        end_date=end_date,
        status_filter="valid",
    )
    return [o for o in all_obs if o.acquisition_date.month == month]


def count_observations(water_body_id: str, zone_id: str) -> int:
    """Return total stored observation count for a zone."""
    return len(get_observations(water_body_id, zone_id=zone_id))


def clear_observations(water_body_id: str) -> None:
    """Clear all stored observations — useful in tests."""
    with _LOCK:
        path = _store_path(water_body_id)
        if path.exists():
            path.unlink()


class HistoricalRepository:
    """
    Class wrapper for baseline repository operations.
    """
    def save_observations(self, observations: List[HistoricalObservation]) -> None:
        save_observations(observations)

    def get_observations(self, water_body_id: str, zone_id: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, status_filter: Optional[str] = None) -> List[HistoricalObservation]:
        return get_observations(water_body_id, zone_id, start_date, end_date, status_filter)

    def get_by_month(self, water_body_id: str, zone_id: str, month: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[HistoricalObservation]:
        return get_by_month(water_body_id, zone_id, month, start_date, end_date)

    def count_observations(self, water_body_id: str, zone_id: str) -> int:
        return count_observations(water_body_id, zone_id)

    def clear(self, water_body_id: str) -> None:
        clear_observations(water_body_id)

