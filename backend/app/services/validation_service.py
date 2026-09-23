"""
ValidationService — Prompt 13

Orchestrates the complete field/lab validation lifecycle:
  1. Create field samples with unique IDs and coordinate validation
  2. Add laboratory results (multiple per sample)
  3. Update validation status
  4. Run comparison via ValidationComparisonService
  5. Seed demo data for demonstration

Scientific boundary preserved throughout.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.schemas.validation import (
    FieldSampleCreate,
    FieldSampleSchema,
    LabResultCreate,
    LabResultSchema,
    ValidationRecordSchema,
    ValidationResultSchema,
    ValidationStatusUpdate,
    ValidationStatusHistorySchema,
    VALIDATION_STATUSES,
)
from app.database.repositories.validation_repository import ValidationRepository
from app.services.validation_comparison_service import ValidationComparisonService
from app.services.validation_feedback_service import ValidationFeedbackService

logger = logging.getLogger(__name__)

_repo       = ValidationRepository()
_comparison = ValidationComparisonService()
_feedback   = ValidationFeedbackService()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_sample_id(water_body_id: str) -> str:
    prefix = water_body_id.upper().replace("-", "")[:4]
    uid    = uuid.uuid4().hex[:6].upper()
    return f"SMP-{prefix}-{uid}"


def _make_validation_id() -> str:
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:6].upper()
    return f"VAL-{ts}-{uid}"


def _make_lab_result_id() -> str:
    uid = uuid.uuid4().hex[:8].upper()
    return f"LAB-{uid}"


def _make_history_id() -> str:
    return f"HST-{uuid.uuid4().hex[:8].upper()}"


class ValidationService:

    def create_field_sample(self, data: FieldSampleCreate) -> FieldSampleSchema:
        """Create a new field sample and corresponding validation record."""
        now          = _now_iso()
        sample_id    = _make_sample_id(data.water_body_id)
        validation_id = _make_validation_id()

        sample_dict: Dict[str, Any] = {
            **data.model_dump(),
            "sample_id":         sample_id,
            "validation_id":     validation_id,
            "validation_status": "FIELD_COLLECTED",
            "created_at":        now,
            "updated_at":        now,
        }
        _repo.save_sample(sample_dict)

        # Create the linked validation record
        val_record: Dict[str, Any] = {
            "validation_id":      validation_id,
            "alert_id":           data.alert_id,
            "analysis_id":        data.analysis_id,
            "report_id":          data.report_id,
            "water_body_id":      data.water_body_id,
            "zone_id":            data.zone_id,
            "scene_id":           data.scene_id,
            "sample_id":          sample_id,
            "sample_date":        data.sample_date,
            "sample_time":        data.sample_time,
            "latitude":           data.latitude,
            "longitude":          data.longitude,
            "sample_type":        data.sample_type,
            "collected_by":       data.collected_by,
            "laboratory_name":    None,
            "laboratory_report_id": None,
            "validation_status":  "FIELD_COLLECTED",
            "notes":              data.notes,
            "created_at":         now,
            "updated_at":         now,
        }
        _repo.save_validation_record(val_record)

        return FieldSampleSchema(**sample_dict)

    def get_field_sample(self, sample_id: str) -> Optional[FieldSampleSchema]:
        data = _repo.get_sample_by_id(sample_id)
        if not data:
            return None
        return FieldSampleSchema(**data)

    def list_samples_by_alert(self, alert_id: str) -> List[FieldSampleSchema]:
        return [FieldSampleSchema(**s) for s in _repo.list_samples_by_alert(alert_id)]

    def list_samples_by_zone(self, zone_id: str) -> List[FieldSampleSchema]:
        return [FieldSampleSchema(**s) for s in _repo.list_samples_by_zone(zone_id)]

    def list_all_samples(self) -> List[FieldSampleSchema]:
        return [FieldSampleSchema(**s) for s in _repo.list_all_samples()]

    def add_lab_result(self, sample_id: str, data: LabResultCreate) -> LabResultSchema:
        """Add a lab result to an existing validation record."""
        sample = _repo.get_sample_by_id(sample_id)
        if not sample:
            raise ValueError(f"Sample '{sample_id}' not found")

        now          = _now_iso()
        lab_result_id = _make_lab_result_id()

        result_dict: Dict[str, Any] = {
            **data.model_dump(),
            "lab_result_id": lab_result_id,
            "created_at":    now,
        }
        # Ensure validation_id matches the sample
        result_dict["validation_id"] = sample["validation_id"]
        _repo.save_lab_result(result_dict)

        # Advance validation status to LAB_AVAILABLE
        self._advance_status(
            validation_id   = sample["validation_id"],
            new_status      = "LAB_AVAILABLE",
            changed_by      = "system",
            reason          = "Lab result added",
        )

        # Update laboratory metadata on validation record
        val = _repo.get_validation_by_id(sample["validation_id"])
        if val:
            if data.laboratory_name:
                val["laboratory_name"] = data.laboratory_name
            if data.laboratory_report_id:
                val["laboratory_report_id"] = data.laboratory_report_id
            val["updated_at"] = now
            _repo.save_validation_record(val)

        return LabResultSchema(**result_dict)

    def get_lab_results(self, sample_id: str) -> List[LabResultSchema]:
        sample = _repo.get_sample_by_id(sample_id)
        if not sample:
            return []
        results = _repo.list_lab_results_by_validation(sample["validation_id"])
        return [LabResultSchema(**r) for r in results]

    def get_validation_record(self, validation_id: str) -> Optional[ValidationRecordSchema]:
        data = _repo.get_validation_by_id(validation_id)
        if not data:
            return None
        return ValidationRecordSchema(**data)

    def get_validations_by_alert(self, alert_id: str) -> List[ValidationRecordSchema]:
        return [ValidationRecordSchema(**v) for v in _repo.get_validation_by_alert(alert_id)]

    def get_validations_by_zone(self, zone_id: str) -> List[ValidationRecordSchema]:
        return [ValidationRecordSchema(**v) for v in _repo.get_validation_by_zone(zone_id)]

    def list_all_validations(self) -> List[ValidationRecordSchema]:
        return [ValidationRecordSchema(**v) for v in _repo.list_all_validations()]

    def update_status(
        self,
        validation_id: str,
        update: ValidationStatusUpdate,
    ) -> ValidationRecordSchema:
        val = _repo.get_validation_by_id(validation_id)
        if not val:
            raise ValueError(f"Validation '{validation_id}' not found")

        old_status = val.get("validation_status", "PENDING")
        now = _now_iso()

        # Save history
        _repo.save_history_record({
            "id":              _make_history_id(),
            "validation_id":   validation_id,
            "previous_status": old_status,
            "new_status":      update.status,
            "changed_at":      now,
            "changed_by":      update.changed_by or "operator",
            "reason":          update.reason,
        })

        val["validation_status"] = update.status
        val["updated_at"]        = now
        _repo.save_validation_record(val)

        # Also update the linked sample
        sample = _repo.get_sample_by_validation_id(validation_id)
        if sample:
            sample["validation_status"] = update.status
            sample["updated_at"]        = now
            _repo.save_sample(sample)

        return ValidationRecordSchema(**val)

    def get_validation_history(self, validation_id: str) -> List[ValidationStatusHistorySchema]:
        records = _repo.get_history_by_validation(validation_id)
        return [ValidationStatusHistorySchema(**r) for r in records]

    def run_comparison(
        self,
        validation_id: str,
        anomaly_context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResultSchema:
        """Run the transparent rule-based comparison for a validation record."""
        val = _repo.get_validation_by_id(validation_id)
        if not val:
            raise ValueError(f"Validation '{validation_id}' not found")

        lab_results = _repo.list_lab_results_by_validation(validation_id)

        result = _comparison.compare(
            validation_record = val,
            lab_results       = lab_results,
            anomaly_context   = anomaly_context,
        )

        # Persist the validation status from comparison result
        if result.validation_status in VALIDATION_STATUSES:
            self._advance_status(
                validation_id = validation_id,
                new_status    = result.validation_status,
                changed_by    = "comparison_engine",
                reason        = "Automatic rule-based comparison",
            )

        # Capture feedback snapshot for future model development
        try:
            feature_snap = {}
            if anomaly_context:
                feature_snap = {
                    "ndti_deviation":              anomaly_context.get("deviation_relative"),
                    "satellite_value":             anomaly_context.get("current_value"),
                    "satellite_baseline":          anomaly_context.get("baseline_median"),
                    "temporal_difference_days":    result.temporal_difference_days,
                    "spatial_relation":            result.spatial_relation,
                    "validation_evidence_score":   result.validation_evidence_score,
                }
            _feedback.create_feedback(
                validation_id    = validation_id,
                alert_id         = val.get("alert_id"),
                analysis_id      = val.get("analysis_id"),
                water_body_id    = val.get("water_body_id", "unknown"),
                zone_id          = val.get("zone_id", "zone-main"),
                feature_snapshot = feature_snap,
                validation_label = result.validation_status,
            )
        except Exception as exc:
            logger.warning(f"Feedback capture failed (non-critical): {exc}")

        return result

    def _advance_status(
        self,
        validation_id: str,
        new_status: str,
        changed_by: str = "system",
        reason: Optional[str] = None,
    ) -> None:
        val = _repo.get_validation_by_id(validation_id)
        if not val:
            return
        old_status = val.get("validation_status", "PENDING")
        if old_status == new_status:
            return

        now = _now_iso()
        _repo.save_history_record({
            "id":              _make_history_id(),
            "validation_id":   validation_id,
            "previous_status": old_status,
            "new_status":      new_status,
            "changed_at":      now,
            "changed_by":      changed_by,
            "reason":          reason,
        })

        val["validation_status"] = new_status
        val["updated_at"]        = now
        _repo.save_validation_record(val)

        sample = _repo.get_sample_by_validation_id(validation_id)
        if sample:
            sample["validation_status"] = new_status
            sample["updated_at"]        = now
            _repo.save_sample(sample)

    # ── Demo data ──────────────────────────────────────────────────────────────

    def get_demo_validation(self) -> Dict[str, Any]:
        """
        Return a deterministic demo validation result.
        Clearly marked as DEMO DATA.
        """
        demo_val_id = "VAL-DEMO-GOSIKHURD-001"
        demo_sample_id = "SMP-GOSI-DEMO01"

        # Return consistent demo structure
        demo_record: Dict[str, Any] = {
            "validation_id":      demo_val_id,
            "alert_id":           "ALT-DEMO-2026-001",
            "analysis_id":        "ANALYSIS-DEMO-001",
            "report_id":          None,
            "water_body_id":      "gosikhurd-reservoir",
            "zone_id":            "zone-c",
            "scene_id":           None,
            "sample_id":          demo_sample_id,
            "sample_date":        "2026-09-21",
            "sample_time":        "09:30",
            "latitude":           20.742,
            "longitude":          79.653,
            "sample_type":        "SURFACE_WATER",
            "collected_by":       "Demo Operator",
            "laboratory_name":    "Demo Water Quality Laboratory",
            "laboratory_report_id": "LAB-DEMO-2026-001",
            "validation_status":  "SUPPORTED",
            "notes":              "DEMO DATA — not a real laboratory result.",
            "created_at":         "2026-09-21T09:30:00+00:00",
            "updated_at":         "2026-09-22T14:00:00+00:00",
        }

        demo_lab_results: List[Dict[str, Any]] = [
            {
                "lab_result_id":      "LAB-DEMO-001",
                "validation_id":      demo_val_id,
                "parameter_name":     "Turbidity",
                "value":              18.4,
                "unit":               "NTU",
                "detection_limit":    None,
                "qualifier":          None,
                "method":             "Nephelometric",
                "measured_at":        "2026-09-22T10:00:00+00:00",
                "laboratory_name":    "Demo Water Quality Laboratory",
                "laboratory_report_id": "LAB-DEMO-2026-001",
                "reference_min":      0.0,
                "reference_max":      10.0,
                "notes":              "DEMO DATA",
                "created_at":         "2026-09-22T10:00:00+00:00",
            },
            {
                "lab_result_id":      "LAB-DEMO-002",
                "validation_id":      demo_val_id,
                "parameter_name":     "TSS",
                "value":              32.0,
                "unit":               "mg/L",
                "detection_limit":    None,
                "qualifier":          None,
                "method":             "Gravimetric",
                "measured_at":        "2026-09-22T10:00:00+00:00",
                "laboratory_name":    "Demo Water Quality Laboratory",
                "laboratory_report_id": "LAB-DEMO-2026-001",
                "reference_min":      None,
                "reference_max":      25.0,
                "notes":              "DEMO DATA",
                "created_at":         "2026-09-22T10:00:00+00:00",
            },
            {
                "lab_result_id":      "LAB-DEMO-003",
                "validation_id":      demo_val_id,
                "parameter_name":     "pH",
                "value":              7.4,
                "unit":               "",
                "detection_limit":    None,
                "qualifier":          None,
                "method":             "Electrochemical",
                "measured_at":        "2026-09-22T10:00:00+00:00",
                "laboratory_name":    "Demo Water Quality Laboratory",
                "laboratory_report_id": "LAB-DEMO-2026-001",
                "reference_min":      6.5,
                "reference_max":      8.5,
                "notes":              "DEMO DATA",
                "created_at":         "2026-09-22T10:00:00+00:00",
            },
        ]

        demo_anomaly_ctx: Dict[str, Any] = {
            "indicator":          "ndti",
            "current_value":      0.150,
            "baseline_median":    0.120,
            "deviation_relative": 0.25,
            "analysis_date":      "2026-09-20",
            "zone_lat":           20.742,
            "zone_lon":           79.653,
        }

        comparison_result = _comparison.compare(
            validation_record = demo_record,
            lab_results       = demo_lab_results,
            anomaly_context   = demo_anomaly_ctx,
        )

        return {
            "data_source_mode":    "DEMO DATA",
            "demo_disclaimer":     (
                "These values are demonstration data only. They do not represent "
                "real field observations or laboratory results."
            ),
            "validation_record":   demo_record,
            "lab_results":         demo_lab_results,
            "anomaly_context":     demo_anomaly_ctx,
            "comparison_result":   comparison_result.model_dump(),
        }
