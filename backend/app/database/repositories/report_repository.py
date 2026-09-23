import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from threading import Lock

logger = logging.getLogger(__name__)

_DATA_DIR = Path(os.environ.get("REPORT_DATA_DIR", "data/reports"))
_LOCK = Lock()


def _store_path(filename: str = "reports.json") -> Path:
    return _DATA_DIR / filename


def _load_reports() -> List[Dict[str, Any]]:
    path = _store_path()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load reports store: {e}")
        return []


def _save_reports(reports: List[Dict[str, Any]]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)


class ReportRepository:

    def get_all(self) -> List[Dict[str, Any]]:
        return _load_reports()

    def get_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        for r in _load_reports():
            if r.get("report_id") == report_id:
                return r
        return None

    def save(self, report_data: Dict[str, Any]) -> None:
        with _LOCK:
            reports = _load_reports()
            rid = report_data.get("report_id")
            idx = next((i for i, r in enumerate(reports) if r.get("report_id") == rid), None)
            if idx is not None:
                reports[idx] = report_data
            else:
                reports.append(report_data)
            _save_reports(reports)
