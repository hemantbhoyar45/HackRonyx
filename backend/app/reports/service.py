"""
ReportGenerationService
-----------------------
Orchestrates the end-to-end report lifecycle:
  1. Validate request
  2. Build data context via ReportDataBuilder
  3. Generate PDF via ReportGenerator
  4. Persist metadata via ReportRepository
  5. Return ReportMetadata
"""
from __future__ import annotations

import uuid
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.reports.data_builder import ReportDataBuilder
from app.reports.generator import ReportGenerator
from app.database.repositories.report_repository import ReportRepository
from app.schemas.report import ReportMetadata, ReportGenerationRequest, ReportPreviewSchema

logger = logging.getLogger(__name__)

_PDF_DIR = Path(os.environ.get("REPORT_PDF_DIR", "data/reports/pdf"))


def _generate_report_id() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:6].upper()
    return f"WQI-REPORT-{ts}-{uid}"


class ReportGenerationService:

    def __init__(self):
        self._builder  = ReportDataBuilder()
        self._renderer = ReportGenerator()
        self._repo     = ReportRepository()

    def generate(self, req: ReportGenerationRequest) -> ReportMetadata:
        report_id = _generate_report_id()
        generated_at = datetime.utcnow().isoformat()

        # --- Build context ---
        if req.report_type == "INVESTIGATION":
            if not req.alert_id:
                raise ValueError("alert_id is required for INVESTIGATION reports")
            ctx = self._builder.build_for_alert(req.alert_id)
        elif req.report_type == "ANALYSIS":
            if not req.water_body_id:
                raise ValueError("water_body_id is required for ANALYSIS reports")
            ctx = self._builder.build_for_analysis(
                water_body_id   = req.water_body_id,
                water_body_name = req.water_body_name or req.water_body_id,
                start_date      = req.start_date or "N/A",
                end_date        = req.end_date or datetime.utcnow().strftime("%Y-%m-%d"),
                scene_id        = req.scene_id,
            )
        else:
            raise ValueError(f"Unknown report_type: {req.report_type}")

        # --- Render PDF ---
        pdf_bytes = self._renderer.generate(ctx, report_id)

        # --- Save PDF to disk ---
        _PDF_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = _PDF_DIR / f"{report_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # --- Persist metadata ---
        meta = ReportMetadata(
            report_id       = report_id,
            report_type     = req.report_type,
            water_body_id   = ctx.get("water_body_id", "unknown"),
            water_body_name = ctx.get("water_body_name", "Unknown"),
            analysis_date   = ctx.get("analysis_date", generated_at[:10]),
            date_range_start= req.start_date,
            date_range_end  = req.end_date,
            alert_id        = req.alert_id,
            generated_at    = generated_at,
            processing_mode = ctx.get("processing_mode", "DEMO DATA"),
            status          = "READY",
            file_path       = str(pdf_path),
        )
        self._repo.save(meta.model_dump())
        return meta

    def get_preview(self, report_id: str) -> ReportPreviewSchema:
        data = self._repo.get_by_id(report_id)
        if not data:
            raise ValueError(f"Report '{report_id}' not found")
        return ReportPreviewSchema(**data)

    def get_pdf_path(self, report_id: str) -> Path:
        data = self._repo.get_by_id(report_id)
        if not data:
            raise ValueError(f"Report '{report_id}' not found")
        path = Path(data.get("file_path", ""))
        if not path.exists():
            raise FileNotFoundError(f"PDF for report '{report_id}' not found on disk")
        return path
