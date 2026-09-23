"""
ReportDataBuilder
-----------------
Assembles a structured data context dict from existing Prompt 03-11 outputs.
This layer isolates PDF-rendering logic from business/analysis logic.
All values come from already-computed results stored in repositories or passed
as arguments.  Missing values are represented as None – the renderer converts
them to 'N/A'.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.repositories.alert_repository import AlertRepository
from app.services.historical_service import HistoricalService
from app.services.anomaly_service import AnomalyService
from app.services.indicator_service import run_indicators
from app.schemas.indicators import IndicatorsRequest
from app.schemas.anomaly import AnomalyRequest
from app.services.priority_queue_service import PriorityQueueService
from app.intelligence.explainability.service import ExplainabilityService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Water-body static metadata
# ---------------------------------------------------------------------------

WATER_BODY_INFO: Dict[str, Dict[str, str]] = {
    "gosikhurd-reservoir": {
        "name": "Gosikhurd Reservoir",
        "type": "Reservoir",
        "state": "Maharashtra, India",
    },
    "godavari-river-segment": {
        "name": "Godavari River – Selected Segment",
        "type": "River Segment",
        "state": "Maharashtra / Telangana, India",
    },
    "wainganga-river-segment": {
        "name": "Wainganga River – Selected Segment",
        "type": "River Segment",
        "state": "Maharashtra / Madhya Pradesh, India",
    },
    "jaikwadi-reservoir": {
        "name": "Jaikwadi Reservoir",
        "type": "Reservoir",
        "state": "Maharashtra, India",
    },
}


def _wb_name(water_body_id: str) -> str:
    info = WATER_BODY_INFO.get(water_body_id, {})
    return info.get("name", water_body_id.replace("-", " ").title())


def _wb_type(water_body_id: str) -> str:
    info = WATER_BODY_INFO.get(water_body_id, {})
    return info.get("type", "Water Body")


def _wb_state(water_body_id: str) -> str:
    info = WATER_BODY_INFO.get(water_body_id, {})
    return info.get("state", "N/A")


# ---------------------------------------------------------------------------

class ReportDataBuilder:
    """
    Constructs a rich data context dictionary that can be passed to
    ReportGenerator.  All external service calls are centralised here.
    """

    def __init__(self):
        self._alert_repo = AlertRepository()
        self._hist_svc   = HistoricalService()
        self._anomaly_svc = AnomalyService()
        self._queue_svc  = PriorityQueueService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_for_alert(self, alert_id: str) -> Dict[str, Any]:
        """Build a full report context from a persisted alert."""
        alert_data = self._alert_repo.get_alert_by_id(alert_id)
        if alert_data is None:
            raise ValueError(f"Alert '{alert_id}' not found")

        water_body_id   = alert_data.get("water_body_id", "unknown")
        analysis_date   = alert_data.get("analysis_date", "N/A")
        zone_id         = alert_data.get("zone_id", "zone-main")
        scene_id        = alert_data.get("scene_id", "SENTINEL2_DEMO")

        # Fetch priority/queue item for this alert (contains indicators etc.)
        priority_data   = self._fetch_priority_data(alert_id)

        # Historical baseline context (2-year window)
        historical_ctx  = self._fetch_historical(water_body_id, zone_id, analysis_date)

        return self._assemble(
            report_type     = "INVESTIGATION",
            water_body_id   = water_body_id,
            water_body_name = _wb_name(water_body_id),
            analysis_date   = analysis_date,
            scene_id        = scene_id,
            alert_data      = alert_data,
            priority_data   = priority_data,
            historical_ctx  = historical_ctx,
        )

    def build_for_analysis(
        self,
        water_body_id: str,
        water_body_name: str,
        start_date: str,
        end_date: str,
        scene_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a report context purely from analysis parameters (no alert needed)."""
        zone_id        = "zone-main"
        analysis_date  = end_date
        sc             = scene_id or "SENTINEL2_DEMO"

        historical_ctx = self._fetch_historical(water_body_id, zone_id, analysis_date)

        # Generate demo anomaly data for this analysis
        priority_data  = self._build_demo_priority(water_body_id, sc, analysis_date)

        return self._assemble(
            report_type     = "ANALYSIS",
            water_body_id   = water_body_id,
            water_body_name = water_body_name or _wb_name(water_body_id),
            analysis_date   = analysis_date,
            scene_id        = sc,
            alert_data      = None,
            priority_data   = priority_data,
            historical_ctx  = historical_ctx,
            start_date      = start_date,
            end_date        = end_date,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_historical(self, water_body_id, zone_id, analysis_date) -> Dict[str, Any]:
        import asyncio
        try:
            end_date   = analysis_date
            start_date = self._two_years_before(end_date)
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                self._hist_svc.get_historical_analysis(
                    water_body_id = water_body_id,
                    zone_id       = zone_id,
                    start_date    = start_date,
                    end_date      = end_date,
                )
            )
            loop.close()

            # result is HistoricalResponse – time_series is a Dict[indicator, List[TimeSeriesPoint]]
            ts_dict = result.time_series or {}
            obs_count = result.valid_observations or 0

            # Build a simple table: date -> indicator values
            # We pivot from per-indicator lists to per-date dict
            date_map: Dict[str, Dict[str, Any]] = {}
            INDICATOR_MAP = {
                "ndti":                     "ndti",
                "suspended_sediment_proxy": "susp_sed",
                "ndci":                     "ndci",
                "fai":                      "fai",
            }
            for ind_key, col in INDICATOR_MAP.items():
                pts = ts_dict.get(ind_key, [])
                for pt in pts:
                    d = pt.date if isinstance(pt.date, str) else str(pt.date)
                    if d not in date_map:
                        date_map[d] = {"date": d}
                    date_map[d][col] = round(pt.median, 4) if pt.median is not None else None

            ts_rows = sorted(date_map.values(), key=lambda x: x["date"])[-24:]

            # Build a simple baseline dict from the last data
            # Use median of medians across all time points for each indicator
            def _compute_baseline_stats(pts_list):
                vals = [p.median for p in pts_list if p.median is not None]
                if not vals:
                    return {}
                import statistics
                med = statistics.median(vals)
                deviations = [abs(v - med) for v in vals]
                mad = statistics.median(deviations) if deviations else 0
                return {"median": round(med, 4), "mad": round(mad, 4)}

            baseline = {}
            for ind_key in INDICATOR_MAP:
                pts = ts_dict.get(ind_key, [])
                if pts:
                    baseline[ind_key] = _compute_baseline_stats(pts)

            return {
                "baseline":      baseline,
                "obs_count":     obs_count,
                "time_series":   ts_rows,
                "start_date":    start_date,
                "end_date":      end_date,
            }
        except Exception as exc:
            logger.warning(f"Historical fetch failed: {exc}")
            return {"baseline": {}, "obs_count": 0, "time_series": [], "start_date": None, "end_date": None}


    def _fetch_priority_data(self, alert_id: str) -> Dict[str, Any]:
        """Try to get the priority queue item and extract indicator data from it."""
        try:
            queue_items = self._queue_svc.get_queue()
            for item in queue_items:
                if item.alert_id == alert_id:
                    ad = item.alert_details
                    return {
                        "priority_score":   item.investigation_priority_score,
                        "priority_band":    item.priority_band,
                        "severity":         item.severity,
                        "confidence":       item.confidence,
                        "primary_driver":   item.primary_driver,
                        "supporting":       [],
                        "evidence_stmts":   [e.model_dump() for e in ad.evidence_statements],
                        "recommendations":  [r.model_dump() for r in ad.recommended_actions],
                        "summary":          ad.summary,
                        "primary_reason":   ad.primary_reason,
                        "indicators":       [],
                    }
        except Exception as exc:
            logger.warning(f"Priority fetch failed: {exc}")
        return {}

    def _build_demo_priority(self, water_body_id, scene_id, analysis_date) -> Dict[str, Any]:
        """Generate a demo priority context for ANALYSIS reports without a stored alert."""
        import asyncio, hashlib

        # Deterministic seeding so the same inputs always give same results
        seed = int(hashlib.md5(f"{water_body_id}{analysis_date}".encode()).hexdigest()[:8], 16)
        score = 30.0 + (seed % 55)  # 30–84
        band = "HIGH" if score >= 60 else "MODERATE" if score >= 40 else "LOW"
        sev  = "HIGH" if score >= 70 else "MODERATE"
        conf = min(95.0, 60.0 + (seed % 30))

        return {
            "priority_score":  round(score, 1),
            "priority_band":   band,
            "severity":        sev,
            "confidence":      round(conf, 1),
            "primary_driver":  "NDTI",
            "supporting":      ["Suspended Sediment Proxy", "NDCI"],
            "evidence_stmts":  [],
            "recommendations": [{"action": "Monitor indicator trends in next satellite pass.", "urgency": "LOW"}],
            "summary":         "Satellite-derived spectral indicators show notable deviation from historical baseline. Potential Water Quality Anomaly detected.",
            "primary_reason":  "Significant deviation detected in NDTI",
            "indicators":      [],
        }

    @staticmethod
    def _assemble(
        *,
        report_type: str,
        water_body_id: str,
        water_body_name: str,
        analysis_date: str,
        scene_id: str,
        alert_data: Optional[Dict[str, Any]],
        priority_data: Dict[str, Any],
        historical_ctx: Dict[str, Any],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Merge all sub-contexts into one flat context dict."""
        alert_id     = (alert_data or {}).get("alert_id")
        alert_status = (alert_data or {}).get("status", "N/A")

        # Indicator table rows
        indicator_rows = ReportDataBuilder._build_indicator_rows(
            priority_data.get("indicators", []),
            historical_ctx.get("baseline", {}),
        )

        return {
            # ---- Report meta ----
            "report_type":      report_type,
            "water_body_id":    water_body_id,
            "water_body_name":  water_body_name,
            "water_body_type":  _wb_type(water_body_id),
            "water_body_state": _wb_state(water_body_id),
            "analysis_date":    analysis_date,
            "start_date":       start_date or historical_ctx.get("start_date"),
            "end_date":         end_date or analysis_date,
            "scene_id":         scene_id,

            # ---- Alert ----
            "alert_id":         alert_id,
            "alert_status":     alert_status,
            "alert_summary":    (alert_data or {}).get("summary", "N/A"),

            # ---- Satellite / preprocessing ----
            "satellite_source": "Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED)",
            "acquisition_date": analysis_date,
            "cloud_pct":        "~8%",      # deterministic demo value
            "valid_pct":        "~92%",
            "obs_quality":      "GOOD",
            "processing_mode":  "DEMO DATA",

            # ---- Water detection ----
            "water_detection_method": "NDWI / MNDWI Combined",
            "detected_water_area":    "Varies by AOI",
            "water_coverage_pct":     "N/A",

            # ---- Priority / Evidence ----
            "priority_score":   priority_data.get("priority_score"),
            "priority_band":    priority_data.get("priority_band"),
            "severity":         priority_data.get("severity"),
            "confidence":       priority_data.get("confidence"),
            "primary_driver":   priority_data.get("primary_driver", "N/A"),
            "supporting_inds":  priority_data.get("supporting", []),
            "evidence_stmts":   priority_data.get("evidence_stmts", []),
            "recommendations":  priority_data.get("recommendations", []),
            "primary_reason":   priority_data.get("primary_reason", "N/A"),
            "exec_summary":     priority_data.get("summary", "N/A"),

            # ---- Historical ----
            "hist_obs_count":   historical_ctx.get("obs_count", 0),
            "hist_start":       historical_ctx.get("start_date"),
            "hist_end":         historical_ctx.get("end_date"),
            "hist_baseline":    historical_ctx.get("baseline", {}),
            "time_series":      historical_ctx.get("time_series", []),

            # ---- Indicator table ----
            "indicator_rows":   indicator_rows,
        }

    @staticmethod
    def _build_indicator_rows(
        indicators: List[Dict],
        baseline: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Construct indicator table rows from priority indicators + baseline."""
        if indicators:
            return [
                {
                    "name":            ind.get("indicator_name", "N/A"),
                    "current":         ReportDataBuilder._fmt(ind.get("current_value")),
                    "baseline":        ReportDataBuilder._fmt(ind.get("baseline_value")),
                    "abs_dev":         ReportDataBuilder._fmt(ind.get("absolute_deviation")),
                    "rel_dev_pct":     ReportDataBuilder._fmt_pct(ind.get("relative_deviation")),
                    "robust_dev":      ReportDataBuilder._fmt(ind.get("robust_deviation")),
                    "direction":       ind.get("direction", "N/A"),
                    "contribution":    ReportDataBuilder._fmt(ind.get("weighted_contribution")),
                }
                for ind in indicators
            ]

        # Fallback: build from baseline dict
        rows = []
        INDICATOR_MAP = {
            "ndti":                     "NDTI (Turbidity Proxy)",
            "suspended_sediment_proxy": "Suspended Sediment Proxy",
            "ndci":                     "NDCI (Chlorophyll Proxy)",
            "fai":                      "FAI (Algal Activity)",
        }
        for key, label in INDICATOR_MAP.items():
            b = baseline.get(key)
            if not b:
                continue
            rows.append({
                "name":         label,
                "current":      "N/A",
                "baseline":     ReportDataBuilder._fmt(b.get("median")),
                "abs_dev":      "N/A",
                "rel_dev_pct":  "N/A",
                "robust_dev":   "N/A",
                "direction":    "N/A",
                "contribution": "N/A",
            })
        return rows

    @staticmethod
    def _fmt(v: Any) -> str:
        if v is None:
            return "N/A"
        try:
            return f"{float(v):.4f}"
        except (TypeError, ValueError):
            return str(v)

    @staticmethod
    def _fmt_pct(v: Any) -> str:
        if v is None:
            return "N/A"
        try:
            return f"{float(v)*100:+.1f}%"
        except (TypeError, ValueError):
            return str(v)

    @staticmethod
    def _two_years_before(date_str: str) -> str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.replace(year=d.year - 2).strftime("%Y-%m-%d")
        except Exception:
            return "2024-01-01"

    @staticmethod
    def _safe_get(d: Any, key: str) -> Any:
        if isinstance(d, dict):
            return d.get(key)
        try:
            return getattr(d, key, None)
        except Exception:
            return None
