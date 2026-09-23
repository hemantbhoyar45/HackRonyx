"""
Validation Repository — JSON flat-file persistence for Prompt 13.

Follows the same pattern as alert_repository.py and report_repository.py.
All five stores:
  - field_samples.json
  - lab_results.json
  - validation_records.json
  - validation_history.json
  - validation_feedback.json
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DATA_DIR = Path(os.environ.get("VALIDATION_DATA_DIR", "data/validation"))
_LOCK = Lock()


def _load(filename: str) -> List[Dict[str, Any]]:
    path = _DATA_DIR / filename
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning(f"Could not load {filename}: {exc}")
        return []


def _save(filename: str, data: List[Dict[str, Any]]) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _upsert(filename: str, id_field: str, record: Dict[str, Any]) -> None:
    with _LOCK:
        records = _load(filename)
        key = record.get(id_field)
        idx = next((i for i, r in enumerate(records) if r.get(id_field) == key), None)
        if idx is not None:
            records[idx] = record
        else:
            records.append(record)
        _save(filename, records)


class ValidationRepository:
    """Unified repository for all validation-related stores."""

    # ── Field Samples ─────────────────────────────────────────────────────────

    def save_sample(self, sample: Dict[str, Any]) -> None:
        _upsert("field_samples.json", "sample_id", sample)

    def get_sample_by_id(self, sample_id: str) -> Optional[Dict[str, Any]]:
        for s in _load("field_samples.json"):
            if s.get("sample_id") == sample_id:
                return s
        return None

    def list_samples_by_alert(self, alert_id: str) -> List[Dict[str, Any]]:
        return [s for s in _load("field_samples.json") if s.get("alert_id") == alert_id]

    def list_samples_by_zone(self, zone_id: str) -> List[Dict[str, Any]]:
        return [s for s in _load("field_samples.json") if s.get("zone_id") == zone_id]

    def get_sample_by_validation_id(self, validation_id: str) -> Optional[Dict[str, Any]]:
        for s in _load("field_samples.json"):
            if s.get("validation_id") == validation_id:
                return s
        return None

    def list_all_samples(self) -> List[Dict[str, Any]]:
        return _load("field_samples.json")

    # ── Lab Results ───────────────────────────────────────────────────────────

    def save_lab_result(self, result: Dict[str, Any]) -> None:
        _upsert("lab_results.json", "lab_result_id", result)

    def get_lab_result_by_id(self, lab_result_id: str) -> Optional[Dict[str, Any]]:
        for r in _load("lab_results.json"):
            if r.get("lab_result_id") == lab_result_id:
                return r
        return None

    def list_lab_results_by_validation(self, validation_id: str) -> List[Dict[str, Any]]:
        return [r for r in _load("lab_results.json") if r.get("validation_id") == validation_id]

    # ── Validation Records ────────────────────────────────────────────────────

    def save_validation_record(self, record: Dict[str, Any]) -> None:
        _upsert("validation_records.json", "validation_id", record)

    def get_validation_by_id(self, validation_id: str) -> Optional[Dict[str, Any]]:
        for r in _load("validation_records.json"):
            if r.get("validation_id") == validation_id:
                return r
        return None

    def get_validation_by_alert(self, alert_id: str) -> List[Dict[str, Any]]:
        return [r for r in _load("validation_records.json") if r.get("alert_id") == alert_id]

    def get_validation_by_zone(self, zone_id: str) -> List[Dict[str, Any]]:
        return [r for r in _load("validation_records.json") if r.get("zone_id") == zone_id]

    def list_all_validations(self) -> List[Dict[str, Any]]:
        return _load("validation_records.json")

    # ── Validation History ────────────────────────────────────────────────────

    def save_history_record(self, record: Dict[str, Any]) -> None:
        with _LOCK:
            history = _load("validation_history.json")
            history.append(record)
            _save("validation_history.json", history)

    def get_history_by_validation(self, validation_id: str) -> List[Dict[str, Any]]:
        return [h for h in _load("validation_history.json") if h.get("validation_id") == validation_id]

    # ── Feedback ──────────────────────────────────────────────────────────────

    def save_feedback(self, feedback: Dict[str, Any]) -> None:
        _upsert("validation_feedback.json", "feedback_id", feedback)

    def get_feedback_by_validation(self, validation_id: str) -> List[Dict[str, Any]]:
        return [f for f in _load("validation_feedback.json") if f.get("validation_id") == validation_id]

    def list_all_feedback(self) -> List[Dict[str, Any]]:
        return _load("validation_feedback.json")
