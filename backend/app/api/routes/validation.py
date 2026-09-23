"""
Validation API Routes — Prompt 13: Ground / Lab Validation & Feedback Loop

Endpoints:
  POST   /api/validation/samples
  GET    /api/validation/samples/{sample_id}
  POST   /api/validation/samples/{sample_id}/lab-results
  GET    /api/validation/samples/{sample_id}/lab-results
  POST   /api/validation/{validation_id}/compare
  GET    /api/validation/{validation_id}
  PATCH  /api/validation/{validation_id}/status
  GET    /api/validation/{validation_id}/history
  GET    /api/validation/by-alert/{alert_id}
  GET    /api/validation/by-zone/{zone_id}
  GET    /api/validation/demo
  GET    /api/validation/feedback
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException

from app.schemas.validation import (
    FieldSampleCreate,
    FieldSampleSchema,
    LabResultCreate,
    LabResultSchema,
    ValidationRecordSchema,
    ValidationResultSchema,
    ValidationStatusUpdate,
    ValidationStatusHistorySchema,
    ValidationListResponse,
)
from app.services.validation_service import ValidationService
from app.services.validation_feedback_service import ValidationFeedbackService

router = APIRouter()
_svc      = ValidationService()
_feedback = ValidationFeedbackService()


# ── Field Samples ──────────────────────────────────────────────────────────────

@router.post("/samples", response_model=FieldSampleSchema)
def create_field_sample(body: FieldSampleCreate):
    """Create a new field sample and linked validation record."""
    try:
        return _svc.create_field_sample(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create sample: {exc}")


@router.get("/samples", response_model=List[FieldSampleSchema])
def list_all_samples():
    """List all field samples."""
    return _svc.list_all_samples()


@router.get("/samples/{sample_id}", response_model=FieldSampleSchema)
def get_field_sample(sample_id: str):
    """Retrieve a single field sample by ID."""
    sample = _svc.get_field_sample(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found")
    return sample


@router.post("/samples/{sample_id}/lab-results", response_model=LabResultSchema)
def add_lab_result(sample_id: str, body: LabResultCreate):
    """Add a laboratory result to an existing field sample."""
    try:
        return _svc.add_lab_result(sample_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to add lab result: {exc}")


@router.get("/samples/{sample_id}/lab-results", response_model=List[LabResultSchema])
def get_lab_results(sample_id: str):
    """Retrieve all lab results for a field sample."""
    return _svc.get_lab_results(sample_id)


# ── Demo Endpoint ──────────────────────────────────────────────────────────────

@router.get("/demo", response_model=Dict[str, Any])
def get_demo_validation():
    """
    Return a fully-worked demonstration validation result.
    Clearly marked as DEMO DATA.
    All values are synthetic and do not represent real observations.
    """
    return _svc.get_demo_validation()

# ── Validation Records ─────────────────────────────────────────────────────────

@router.get("/validations", response_model=ValidationListResponse)
def list_all_validations():
    """List all validation records."""
    items = _svc.list_all_validations()
    return ValidationListResponse(items=items, total=len(items))

@router.get("/{validation_id}", response_model=ValidationRecordSchema)
def get_validation(validation_id: str):
    """Retrieve a single validation record."""
    val = _svc.get_validation_record(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail=f"Validation '{validation_id}' not found")
    return val


@router.patch("/{validation_id}/status", response_model=ValidationRecordSchema)
def update_validation_status(validation_id: str, body: ValidationStatusUpdate):
    """Update the status of a validation record."""
    try:
        return _svc.update_status(validation_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{validation_id}/history", response_model=List[ValidationStatusHistorySchema])
def get_validation_history(validation_id: str):
    """Retrieve status change history for a validation record."""
    return _svc.get_validation_history(validation_id)


@router.post("/{validation_id}/compare", response_model=ValidationResultSchema)
def run_comparison(
    validation_id:   str,
    anomaly_context: Optional[Dict[str, Any]] = Body(default=None),
):
    """
    Run the transparent rule-based validation comparison.
    Optionally accepts satellite anomaly context in the request body.
    """
    try:
        return _svc.run_comparison(validation_id, anomaly_context)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Lookup by Alert / Zone ─────────────────────────────────────────────────────

@router.get("/by-alert/{alert_id}", response_model=List[ValidationRecordSchema])
def get_validations_by_alert(alert_id: str):
    """Get all validation records linked to a specific alert."""
    return _svc.get_validations_by_alert(alert_id)


@router.get("/by-zone/{zone_id}", response_model=List[ValidationRecordSchema])
def get_validations_by_zone(zone_id: str):
    """Get all validation records linked to a specific zone."""
    return _svc.get_validations_by_zone(zone_id)





# ── Feedback ───────────────────────────────────────────────────────────────────

@router.get("/feedback", response_model=List[Dict[str, Any]])
def list_feedback():
    """List all validation feedback snapshots (for future model development)."""
    return _feedback.list_all_feedback()
