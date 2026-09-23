import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from threading import Lock

logger = logging.getLogger(__name__)

_DATA_DIR = Path(os.environ.get("ALERT_DATA_DIR", "data/alerts"))
_LOCK = Lock()

def _store_path(filename: str = "alerts.json") -> Path:
    return _DATA_DIR / filename

def _load_alerts() -> List[Dict[str, Any]]:
    path = _store_path("alerts.json")
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load alerts store: {e}")
        return []

def _save_alerts(alerts: List[Dict[str, Any]]) -> None:
    path = _store_path("alerts.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

def _load_history() -> List[Dict[str, Any]]:
    path = _store_path("alert_history.json")
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load alert history store: {e}")
        return []

def _save_history(history: List[Dict[str, Any]]) -> None:
    path = _store_path("alert_history.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

class AlertRepository:
    def get_all_alerts(self) -> List[Dict[str, Any]]:
        return _load_alerts()

    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        alerts = _load_alerts()
        for alert in alerts:
            if alert.get("alert_id") == alert_id:
                return alert
        return None

    def save_alert(self, alert_data: Dict[str, Any]) -> None:
        with _LOCK:
            alerts = _load_alerts()
            alert_id = alert_data.get("alert_id")
            
            # Upsert
            existing_idx = next((i for i, a in enumerate(alerts) if a.get("alert_id") == alert_id), None)
            if existing_idx is not None:
                alerts[existing_idx] = alert_data
            else:
                alerts.append(alert_data)
                
            _save_alerts(alerts)

    def save_history_record(self, history_data: Dict[str, Any]) -> None:
        with _LOCK:
            history = _load_history()
            history.append(history_data)
            _save_history(history)

    def get_alert_history(self, alert_id: str) -> List[Dict[str, Any]]:
        history = _load_history()
        return [h for h in history if h.get("alert_id") == alert_id]
