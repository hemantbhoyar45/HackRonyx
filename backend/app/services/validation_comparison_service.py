"""
ValidationComparisonService — Prompt 13

Transparent rule-based validation engine.
Compares satellite anomaly observations with field/laboratory evidence.

Scientific boundary:
  - SUPPORTED means compatible directional evidence, NOT pollution confirmation.
  - NOT_SUPPORTED means available evidence does not support the satellite anomaly.
  - INCONCLUSIVE means insufficient, mixed, or out-of-window evidence.

Configuration (prototype/hackathon parameters — documented as such):
  VALIDATION_MATCH_WINDOW_DAYS = 3
  SPATIAL_MATCH_TOLERANCE_METERS = 1000

Related-indicator mapping (conceptual, not direct equivalence):
  ndti                  → turbidity
  suspended_sediment_proxy → tss
  ndci                  → chlorophyll_a
  fai                   → algal_activity
"""
from __future__ import annotations

import logging
import math
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from app.schemas.validation import (
    ValidationResultSchema,
    RELATED_INDICATOR_MAP,
    VALIDATION_STATUSES,
)

logger = logging.getLogger(__name__)

# ── Configurable parameters (prototype / hackathon values) ────────────────────
VALIDATION_MATCH_WINDOW_DAYS: int = 3
SPATIAL_MATCH_TOLERANCE_METERS: float = 1000.0

# Alert zone radius approximation (meters) for demonstration
_ALERT_ZONE_RADIUS_M = 2000.0

_SCIENTIFIC_NOTE = (
    "This validation result reflects available field and laboratory observations "
    "associated with the investigated zone. It does not independently confirm "
    "pollution, contamination, or identify a specific source. "
    "Satellite-observable anomalies and laboratory measurements are distinct "
    "evidence sources that may be conceptually related but are not directly "
    "equivalent measurements."
)


# ── Utility functions ─────────────────────────────────────────────────────────

def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in metres between two WGS-84 points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _temporal_diff_days(sample_date_str: str, analysis_date_str: str) -> Optional[float]:
    try:
        s = date.fromisoformat(sample_date_str)
        a = date.fromisoformat(analysis_date_str)
        return abs((s - a).days)
    except Exception:
        return None


def _temporal_category(diff_days: Optional[float]) -> str:
    if diff_days is None:
        return "OUTSIDE_PREFERRED_WINDOW"
    if diff_days == 0:
        return "SAME_DAY"
    if diff_days <= 1:
        return "WITHIN_1_DAY"
    if diff_days <= VALIDATION_MATCH_WINDOW_DAYS:
        return "WITHIN_3_DAYS"
    return "OUTSIDE_PREFERRED_WINDOW"


def _spatial_category(distance_m: Optional[float]) -> str:
    if distance_m is None:
        return "OUTSIDE_ALERT_ZONE"
    if distance_m <= _ALERT_ZONE_RADIUS_M:
        return "INSIDE_ALERT_ZONE"
    if distance_m <= _ALERT_ZONE_RADIUS_M + SPATIAL_MATCH_TOLERANCE_METERS:
        return "NEAR_ALERT_ZONE"
    return "OUTSIDE_ALERT_ZONE"


def _find_related_lab_result(
    lab_results: List[Dict[str, Any]],
    satellite_indicator: str,
) -> Optional[Dict[str, Any]]:
    """Find the best matching lab result for a satellite indicator."""
    related_param = RELATED_INDICATOR_MAP.get(satellite_indicator.lower(), "")
    if not related_param:
        return None
    for r in lab_results:
        param = r.get("parameter_name", "").lower().replace(" ", "_").replace("-", "_")
        if param == related_param or related_param in param:
            return r
    return None


def _directional_compatible(
    satellite_deviation: Optional[float],
    lab_value: Optional[float],
    lab_reference_min: Optional[float],
    lab_reference_max: Optional[float],
) -> Optional[bool]:
    """
    Returns True if satellite and lab show compatible directional evidence.
    Returns False if they conflict.
    Returns None if insufficient data.

    Rules:
      - Positive satellite deviation → elevated satellite indicator.
      - If lab reference range available: lab > reference_max → elevated.
      - If no reference range: cannot determine direction from lab alone → None.
    """
    if satellite_deviation is None:
        return None
    if lab_value is None:
        return None

    sat_elevated = satellite_deviation > 0

    if lab_reference_max is not None:
        lab_elevated = lab_value > lab_reference_max
        return sat_elevated == lab_elevated

    if lab_reference_min is not None:
        lab_below = lab_value < lab_reference_min
        # If satellite is elevated but lab is below min, that conflicts
        if sat_elevated and lab_below:
            return False
        # Otherwise inconclusive on direction
        return None

    return None  # no reference data — cannot establish direction


class ValidationComparisonService:
    """
    Compares satellite anomaly observations with field/laboratory evidence.

    This is a transparent, rule-based system. No machine-learning inference.
    """

    def compare(
        self,
        validation_record: Dict[str, Any],
        lab_results: List[Dict[str, Any]],
        anomaly_context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResultSchema:
        """
        Run the validation comparison and return a ValidationResultSchema.

        Parameters
        ----------
        validation_record : dict   — the FieldSample / ValidationRecord data
        lab_results       : list   — list of LabResult dicts for this sample
        anomaly_context   : dict   — optional satellite anomaly data
        """
        validation_id = validation_record.get("validation_id", "unknown")
        sample_date   = validation_record.get("sample_date")
        lat  = validation_record.get("latitude")
        lon  = validation_record.get("longitude")

        # ── Satellite context ──────────────────────────────────────────────
        sat_indicator   = None
        sat_value       = None
        sat_baseline    = None
        sat_deviation   = None
        sat_date        = None

        if anomaly_context:
            sat_indicator = anomaly_context.get("indicator")
            sat_value     = anomaly_context.get("current_value")
            sat_baseline  = anomaly_context.get("baseline_median")
            sat_deviation = anomaly_context.get("deviation_relative")
            sat_date      = anomaly_context.get("analysis_date")

        # ── Temporal matching ──────────────────────────────────────────────
        temporal_diff  = _temporal_diff_days(sample_date, sat_date) if sat_date else None
        temporal_cat   = _temporal_category(temporal_diff)
        temporal_ok    = temporal_cat in ("SAME_DAY", "WITHIN_1_DAY", "WITHIN_3_DAYS")

        # ── Spatial matching ───────────────────────────────────────────────
        distance_m = None
        if lat is not None and lon is not None and anomaly_context:
            zone_lat = anomaly_context.get("zone_lat", lat)
            zone_lon = anomaly_context.get("zone_lon", lon)
            distance_m = _haversine_m(lat, lon, zone_lat, zone_lon)
        spatial_cat = _spatial_category(distance_m)
        spatial_ok  = spatial_cat in ("INSIDE_ALERT_ZONE", "NEAR_ALERT_ZONE")

        # ── Lab evidence ───────────────────────────────────────────────────
        related_lab = None
        lab_value   = None
        lab_unit    = None
        related_param_name = None

        if sat_indicator:
            related_lab = _find_related_lab_result(lab_results, sat_indicator)
        elif lab_results:
            related_lab = lab_results[0]  # fallback: use first available

        if related_lab:
            lab_value  = related_lab.get("value")
            lab_unit   = related_lab.get("unit")
            related_param_name = related_lab.get("parameter_name")

        lab_available = related_lab is not None and lab_value is not None

        # ── Directional compatibility ──────────────────────────────────────
        ref_min = related_lab.get("reference_min") if related_lab else None
        ref_max = related_lab.get("reference_max") if related_lab else None
        direction_ok = _directional_compatible(sat_deviation, lab_value, ref_min, ref_max)

        # ── Anomaly exists flag ────────────────────────────────────────────
        anomaly_exists = sat_deviation is not None and abs(sat_deviation) > 0.05

        # ── Validation Rule Engine ─────────────────────────────────────────
        status, explanation = self._apply_rules(
            anomaly_exists   = anomaly_exists,
            lab_available    = lab_available,
            temporal_ok      = temporal_ok,
            spatial_ok       = spatial_ok,
            direction_ok     = direction_ok,
            temporal_cat     = temporal_cat,
            spatial_cat      = spatial_cat,
            sat_indicator    = sat_indicator,
            sat_deviation    = sat_deviation,
            related_param    = related_param_name,
            lab_value        = lab_value,
            lab_unit         = lab_unit,
        )

        # ── Evidence Score (0–100) — NOT a pollution probability ───────────
        score = self._compute_evidence_score(
            anomaly_exists = anomaly_exists,
            lab_available  = lab_available,
            temporal_ok    = temporal_ok,
            spatial_ok     = spatial_ok,
            direction_ok   = direction_ok,
            temporal_diff  = temporal_diff,
        )

        # ── Data quality labels ────────────────────────────────────────────
        data_quality = {
            "satellite_observation": "AVAILABLE" if anomaly_exists else (
                "AVAILABLE_NO_SIGNIFICANT_ANOMALY" if sat_value is not None else "NOT_AVAILABLE"
            ),
            "laboratory_result": "AVAILABLE" if lab_available else "NOT_AVAILABLE",
            "temporal_match":  f"{temporal_cat} — {temporal_diff:.0f} day(s)" if temporal_diff is not None else "UNKNOWN",
            "spatial_match":   spatial_cat,
            "related_parameter": "AVAILABLE" if related_lab else "NOT_AVAILABLE",
        }

        return ValidationResultSchema(
            validation_id            = validation_id,
            validation_status        = status,
            satellite_indicator      = sat_indicator,
            related_lab_parameter    = related_param_name,
            satellite_value          = sat_value,
            satellite_baseline       = sat_baseline,
            satellite_deviation      = sat_deviation,
            lab_value                = lab_value,
            lab_unit                 = lab_unit,
            temporal_relation        = temporal_cat,
            temporal_difference_days = temporal_diff,
            spatial_relation         = spatial_cat,
            spatial_distance_m       = round(distance_m, 1) if distance_m else None,
            validation_evidence_score = round(score, 1),
            explanation              = explanation,
            scientific_note          = _SCIENTIFIC_NOTE,
            data_quality             = data_quality,
        )

    # ── Rule Engine ────────────────────────────────────────────────────────────

    def _apply_rules(
        self,
        anomaly_exists: bool,
        lab_available: bool,
        temporal_ok: bool,
        spatial_ok: bool,
        direction_ok: Optional[bool],
        temporal_cat: str,
        spatial_cat: str,
        sat_indicator: Optional[str],
        sat_deviation: Optional[float],
        related_param: Optional[str],
        lab_value: Optional[float],
        lab_unit: Optional[str],
    ) -> tuple[str, str]:
        """
        Returns (status, explanation) using transparent, documented rules.
        """
        dev_pct = f"{sat_deviation * 100:+.1f}%" if sat_deviation is not None else "unknown"
        lab_str = f"{lab_value} {lab_unit}" if lab_value is not None else "not available"
        ind_str = sat_indicator.upper() if sat_indicator else "satellite indicator"
        prm_str = related_param if related_param else "related parameter"

        # Rule 1: No satellite anomaly
        if not anomaly_exists:
            if not lab_available:
                explanation = (
                    f"No significant satellite anomaly was detected and no laboratory "
                    f"result is available. Validation status is inconclusive."
                )
            else:
                explanation = (
                    f"No significant satellite anomaly was detected ({ind_str} deviation: {dev_pct}). "
                    f"Laboratory result for {prm_str} is {lab_str}. "
                    f"With no satellite anomaly to validate, the status is inconclusive."
                )
            return "INCONCLUSIVE", explanation

        # Rule 2: Anomaly exists but no lab data
        if not lab_available:
            explanation = (
                f"Satellite {ind_str} showed a deviation of {dev_pct} from the historical baseline. "
                f"No related laboratory measurement is available for comparison. "
                f"Validation remains inconclusive due to missing laboratory evidence."
            )
            return "INCONCLUSIVE", explanation

        # Rule 3: Lab data available but outside temporal window
        if not temporal_ok:
            explanation = (
                f"Satellite {ind_str} showed a deviation of {dev_pct}. "
                f"Laboratory {prm_str} result is {lab_str}. "
                f"However, the temporal difference ({temporal_cat.lower().replace('_', ' ')}) "
                f"exceeds the configured validation window ({VALIDATION_MATCH_WINDOW_DAYS} days). "
                f"Direct comparison is not reliable. Validation status is inconclusive."
            )
            return "INCONCLUSIVE", explanation

        # Rule 4: Lab data available but outside spatial tolerance
        if not spatial_ok:
            explanation = (
                f"Satellite {ind_str} showed a deviation of {dev_pct}. "
                f"Laboratory {prm_str} result is {lab_str} ({temporal_cat.lower().replace('_', ' ')}). "
                f"The sample location is {spatial_cat.lower().replace('_', ' ')}. "
                f"Spatial mismatch reduces the relevance of direct comparison. "
                f"Validation status is inconclusive."
            )
            return "INCONCLUSIVE", explanation

        # Rule 5: All conditions met — check directional evidence
        if direction_ok is True:
            explanation = (
                f"Satellite {ind_str} showed a positive deviation of {dev_pct} from its historical baseline. "
                f"A {prm_str} laboratory result of {lab_str} was available from a sample collected "
                f"{temporal_cat.lower().replace('_', ' ')} after the satellite observation, "
                f"located {spatial_cat.lower().replace('_', ' ')}. "
                f"The available observations show compatible directional evidence. "
                f"This supports the satellite-observable anomaly, but does not independently "
                f"establish contamination or identify a source."
            )
            return "SUPPORTED", explanation

        if direction_ok is False:
            explanation = (
                f"Satellite {ind_str} showed a deviation of {dev_pct}. "
                f"Laboratory {prm_str} result of {lab_str} was collected "
                f"{temporal_cat.lower().replace('_', ' ')}, located {spatial_cat.lower().replace('_', ' ')}. "
                f"The available laboratory evidence does not show compatible directional evidence "
                f"with the satellite-observable anomaly. "
                f"This does not confirm the anomaly, but also does not confirm absence of a problem."
            )
            return "NOT_SUPPORTED", explanation

        # direction_ok is None — insufficient reference data for direction
        explanation = (
            f"Satellite {ind_str} showed a deviation of {dev_pct}. "
            f"Laboratory {prm_str} result of {lab_str} was collected "
            f"{temporal_cat.lower().replace('_', ' ')}, located {spatial_cat.lower().replace('_', ' ')}. "
            f"Sufficient reference range data is not available to determine directional compatibility. "
            f"Validation status is inconclusive."
        )
        return "INCONCLUSIVE", explanation

    # ── Evidence Score ─────────────────────────────────────────────────────────

    def _compute_evidence_score(
        self,
        anomaly_exists: bool,
        lab_available: bool,
        temporal_ok: bool,
        spatial_ok: bool,
        direction_ok: Optional[bool],
        temporal_diff: Optional[float],
    ) -> float:
        """
        Compute a validation_evidence_score (0–100).

        THIS IS NOT A POLLUTION PROBABILITY.
        It represents the degree of available evidence supporting the satellite-observable anomaly.
        """
        score = 0.0

        if anomaly_exists:
            score += 20.0

        if lab_available:
            score += 25.0

        if temporal_ok:
            if temporal_diff is not None:
                if temporal_diff == 0:
                    score += 25.0
                elif temporal_diff <= 1:
                    score += 20.0
                elif temporal_diff <= VALIDATION_MATCH_WINDOW_DAYS:
                    score += 15.0
            else:
                score += 10.0

        if spatial_ok:
            score += 20.0

        if direction_ok is True:
            score += 10.0
        elif direction_ok is False:
            score = max(0.0, score - 15.0)

        return min(score, 100.0)
