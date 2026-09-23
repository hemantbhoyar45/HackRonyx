"""
Pydantic schemas for Prompt 13: Ground / Lab Validation & Feedback Loop.

Scientific boundary:
  - These schemas represent field and laboratory observations.
  - No schema confirms pollution, contamination, or specific discharge sources.
  - Satellite observations and laboratory measurements are kept as distinct
    evidence sources at all times.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import math


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

SAMPLE_TYPES = [
    "SURFACE_WATER",
    "RESERVOIR_WATER",
    "RIVER_WATER",
    "LAKE_WATER",
    "OTHER",
]

VALIDATION_STATUSES = [
    "PENDING",
    "FIELD_COLLECTED",
    "LAB_PENDING",
    "LAB_AVAILABLE",
    "SUPPORTED",
    "NOT_SUPPORTED",
    "INCONCLUSIVE",
    "REVIEW_REQUIRED",
]

LAB_QUALIFIERS = ["<DL", ">DL", "ND", "Detected", "Not Detected", None]

SPATIAL_RELATIONS = ["INSIDE_ALERT_ZONE", "NEAR_ALERT_ZONE", "OUTSIDE_ALERT_ZONE"]

TEMPORAL_CATEGORIES = [
    "SAME_DAY",
    "WITHIN_1_DAY",
    "WITHIN_3_DAYS",
    "OUTSIDE_PREFERRED_WINDOW",
]

# Configurable related-indicator mapping (satellite → lab)
# These are related parameters, NOT direct measurement equivalents.
RELATED_INDICATOR_MAP: Dict[str, str] = {
    "ndti": "turbidity",
    "suspended_sediment_proxy": "tss",
    "ndci": "chlorophyll_a",
    "fai": "algal_activity",
}


# ──────────────────────────────────────────────────────────────────────────────
# Field Sample
# ──────────────────────────────────────────────────────────────────────────────

class FieldSampleCreate(BaseModel):
    """Request body for creating a new field sample."""
    alert_id:    Optional[str] = None
    analysis_id: Optional[str] = None
    report_id:   Optional[str] = None

    water_body_id: str
    zone_id:       str = "zone-main"
    scene_id:      Optional[str] = None

    sample_date: str          # ISO date: YYYY-MM-DD
    sample_time: Optional[str] = None  # HH:MM

    latitude:  float
    longitude: float

    sample_type: str = "SURFACE_WATER"

    collected_by: Optional[str] = None
    notes:        Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("longitude must be between -180 and 180")
        return v

    @field_validator("sample_type")
    @classmethod
    def validate_sample_type(cls, v: str) -> str:
        if v not in SAMPLE_TYPES:
            raise ValueError(f"sample_type must be one of {SAMPLE_TYPES}")
        return v


class FieldSampleSchema(FieldSampleCreate):
    """Full field sample record as stored/returned."""
    sample_id:         str
    validation_id:     str
    validation_status: str = "FIELD_COLLECTED"
    created_at:        str
    updated_at:        str


# ──────────────────────────────────────────────────────────────────────────────
# Lab Result
# ──────────────────────────────────────────────────────────────────────────────

class LabResultCreate(BaseModel):
    """Request body for adding a lab result to a validation record."""
    validation_id: str

    parameter_name: str       # e.g. "Turbidity", "pH", "TSS"

    value:         Optional[float] = None   # None allowed when qualifier-only
    unit:          str                       # e.g. "NTU", "mg/L"

    detection_limit:   Optional[float] = None
    qualifier:         Optional[str]  = None  # "<DL", "ND", etc.

    method:            Optional[str] = None
    measured_at:       Optional[str] = None   # ISO datetime

    laboratory_name:      Optional[str] = None
    laboratory_report_id: Optional[str] = None

    reference_min: Optional[float] = None
    reference_max: Optional[float] = None

    notes: Optional[str] = None

    @field_validator("parameter_name")
    @classmethod
    def validate_param(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("parameter_name must not be empty")
        return v.strip()


class LabResultSchema(LabResultCreate):
    """Full lab result record."""
    lab_result_id: str
    created_at:    str


# ──────────────────────────────────────────────────────────────────────────────
# Validation Record
# ──────────────────────────────────────────────────────────────────────────────

class ValidationRecordSchema(BaseModel):
    """Core validation entity linking satellite, field, and lab evidence."""
    validation_id: str

    alert_id:    Optional[str] = None
    analysis_id: Optional[str] = None
    report_id:   Optional[str] = None

    water_body_id: str
    zone_id:       str
    scene_id:      Optional[str] = None

    sample_id: str
    sample_date: str
    sample_time: Optional[str] = None

    latitude:  Optional[float] = None
    longitude: Optional[float] = None

    sample_type: str

    collected_by:         Optional[str] = None
    laboratory_name:      Optional[str] = None
    laboratory_report_id: Optional[str] = None

    validation_status: str = "PENDING"

    notes:      Optional[str] = None
    created_at: str
    updated_at: str


# ──────────────────────────────────────────────────────────────────────────────
# Validation Result (comparison output)
# ──────────────────────────────────────────────────────────────────────────────

class ValidationResultSchema(BaseModel):
    """Output of the ValidationComparisonService."""
    validation_id: str

    validation_status: str

    satellite_indicator:   Optional[str]   = None
    related_lab_parameter: Optional[str]   = None

    satellite_value:    Optional[float] = None
    satellite_baseline: Optional[float] = None
    satellite_deviation: Optional[float] = None  # fractional, e.g. +0.25

    lab_value: Optional[float] = None
    lab_unit:  Optional[str]   = None

    temporal_relation:      Optional[str]   = None
    temporal_difference_days: Optional[float] = None

    spatial_relation:    Optional[str]   = None
    spatial_distance_m:  Optional[float] = None

    validation_evidence_score: Optional[float] = None  # 0–100

    explanation:    str
    scientific_note: str = (
        "This validation result reflects available field and laboratory "
        "observations associated with the investigated zone. It does not "
        "independently confirm pollution, contamination, or identify a specific "
        "source. Satellite-observable anomalies and laboratory measurements are "
        "distinct evidence sources."
    )

    data_quality: Optional[Dict[str, str]] = None


# ──────────────────────────────────────────────────────────────────────────────
# Status update
# ──────────────────────────────────────────────────────────────────────────────

class ValidationStatusUpdate(BaseModel):
    status:     str
    changed_by: Optional[str] = "operator"
    reason:     Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALIDATION_STATUSES:
            raise ValueError(f"status must be one of {VALIDATION_STATUSES}")
        return v


class ValidationStatusHistorySchema(BaseModel):
    id:              str
    validation_id:   str
    previous_status: str
    new_status:      str
    changed_at:      str
    changed_by:      str
    reason:          Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Feedback (for future model development)
# ──────────────────────────────────────────────────────────────────────────────

class ValidationFeedbackSchema(BaseModel):
    """
    Feature snapshot for future model development.
    Only stores; never triggers model retraining.
    """
    feedback_id:   str
    validation_id: str
    analysis_id:   Optional[str] = None
    alert_id:      Optional[str] = None
    water_body_id: str
    zone_id:       str

    feature_snapshot: Dict[str, Any]  # satellite features at time of validation

    validation_label: str   # SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE

    created_at: str


# ──────────────────────────────────────────────────────────────────────────────
# List responses
# ──────────────────────────────────────────────────────────────────────────────

class ValidationListResponse(BaseModel):
    items: List[ValidationRecordSchema]
    total: int
