"""
ValidationFeedbackService — Prompt 13

Stores structured feature snapshots for future model development.
DOES NOT train any model. DOES NOT trigger retraining.
Stores only actual available values.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.database.repositories.validation_repository import ValidationRepository

logger = logging.getLogger(__name__)
_repo = ValidationRepository()


class ValidationFeedbackService:

    def create_feedback(
        self,
        validation_id:    str,
        water_body_id:    str,
        zone_id:          str,
        feature_snapshot: Dict[str, Any],
        validation_label: str,
        alert_id:         Optional[str] = None,
        analysis_id:      Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Store a feature snapshot for future model development.
        Only stores available values — does not fabricate missing features.
        """
        now         = datetime.now(timezone.utc).isoformat()
        feedback_id = f"FBK-{uuid.uuid4().hex[:8].upper()}"

        # Clean: remove None values from snapshot
        clean_snapshot = {k: v for k, v in feature_snapshot.items() if v is not None}

        record: Dict[str, Any] = {
            "feedback_id":      feedback_id,
            "validation_id":    validation_id,
            "analysis_id":      analysis_id,
            "alert_id":         alert_id,
            "water_body_id":    water_body_id,
            "zone_id":          zone_id,
            "feature_snapshot": clean_snapshot,
            "validation_label": validation_label,
            "created_at":       now,
        }
        _repo.save_feedback(record)
        logger.info(f"Feedback snapshot stored: {feedback_id} label={validation_label}")
        return record

    def get_feedback_for_validation(self, validation_id: str) -> list:
        return _repo.get_feedback_by_validation(validation_id)

    def list_all_feedback(self) -> list:
        return _repo.list_all_feedback()
