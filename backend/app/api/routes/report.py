from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.report import ReportGenerationRequest, ReportMetadata, ReportPreviewSchema
from app.reports.service import ReportGenerationService

router = APIRouter()
_svc = ReportGenerationService()


@router.post("/generate", response_model=ReportMetadata)
def generate_report(req: ReportGenerationRequest):
    """
    Generate a new PDF report for an analysis or investigation alert.
    Returns report metadata including the report_id to use for download.
    """
    try:
        return _svc.generate(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")


@router.get("/{report_id}/preview", response_model=ReportPreviewSchema)
def preview_report(report_id: str):
    """Return metadata for a generated report (for frontend preview before download)."""
    try:
        return _svc.get_preview(report_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{report_id}/download")
def download_report(report_id: str):
    """Stream the generated PDF report as an attachment."""
    try:
        pdf_path = _svc.get_pdf_path(report_id)
        return FileResponse(
            path     = str(pdf_path),
            media_type = "application/pdf",
            headers  = {
                "Content-Disposition": f'attachment; filename="{report_id}.pdf"'
            },
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
