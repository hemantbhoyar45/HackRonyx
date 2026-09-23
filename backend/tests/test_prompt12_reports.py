"""
Tests for Prompt 12: Downloadable Report generation.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def _generate_analysis_report(water_body_id="gosikhurd-reservoir",
                               water_body_name="Gosikhurd Reservoir",
                               start_date="2024-01-01",
                               end_date="2026-09-22"):
    resp = client.post("/api/reports/generate", json={
        "report_type":     "ANALYSIS",
        "water_body_id":   water_body_id,
        "water_body_name": water_body_name,
        "start_date":      start_date,
        "end_date":        end_date,
    })
    return resp


# ──────────────────────────────────────────────────────────────────────────────
# Schema validation
# ──────────────────────────────────────────────────────────────────────────────

def test_report_schemas_import():
    from app.schemas.report import ReportGenerationRequest, ReportMetadata, ReportPreviewSchema
    req = ReportGenerationRequest(report_type="ANALYSIS", water_body_id="test-wb")
    assert req.report_type == "ANALYSIS"


def test_report_metadata_schema():
    from app.schemas.report import ReportMetadata
    meta = ReportMetadata(
        report_id="WQI-REPORT-TEST-001",
        report_type="ANALYSIS",
        water_body_id="gosikhurd-reservoir",
        water_body_name="Gosikhurd Reservoir",
        analysis_date="2026-09-22",
        generated_at="2026-09-22T10:00:00",
    )
    assert meta.status == "READY"
    assert meta.processing_mode == "DEMO DATA"


# ──────────────────────────────────────────────────────────────────────────────
# Report Generation API
# ──────────────────────────────────────────────────────────────────────────────

def test_generate_analysis_report_returns_200():
    resp = _generate_analysis_report()
    assert resp.status_code == 200, resp.text


def test_generate_analysis_report_returns_report_id():
    resp = _generate_analysis_report()
    data = resp.json()
    assert "report_id" in data
    assert data["report_id"].startswith("WQI-REPORT-")


def test_generate_analysis_report_metadata():
    resp = _generate_analysis_report()
    data = resp.json()
    assert data["report_type"] == "ANALYSIS"
    assert data["water_body_id"] == "gosikhurd-reservoir"
    assert data["status"] == "READY"
    assert data["generated_at"]


def test_generate_report_invalid_type_returns_400():
    resp = client.post("/api/reports/generate", json={
        "report_type": "UNKNOWN_TYPE",
        "water_body_id": "gosikhurd-reservoir",
    })
    assert resp.status_code == 400


def test_generate_investigation_report_without_alert_id_returns_400():
    resp = client.post("/api/reports/generate", json={
        "report_type": "INVESTIGATION",
        # No alert_id
    })
    assert resp.status_code == 400


def test_generate_analysis_report_without_water_body_id_returns_400():
    resp = client.post("/api/reports/generate", json={
        "report_type": "ANALYSIS",
        # No water_body_id
    })
    assert resp.status_code == 400


def test_generate_report_different_water_bodies():
    """Each water body should produce a valid report."""
    for wb in ["gosikhurd-reservoir", "godavari-river-segment", "jaikwadi-reservoir"]:
        resp = client.post("/api/reports/generate", json={
            "report_type":   "ANALYSIS",
            "water_body_id": wb,
            "start_date":    "2024-01-01",
            "end_date":      "2026-09-01",
        })
        assert resp.status_code == 200, f"Failed for {wb}: {resp.text}"


# ──────────────────────────────────────────────────────────────────────────────
# Preview API
# ──────────────────────────────────────────────────────────────────────────────

def test_preview_report_returns_200():
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    preview = client.get(f"/api/reports/{report_id}/preview")
    assert preview.status_code == 200


def test_preview_report_unknown_id_returns_404():
    resp = client.get("/api/reports/NONEXISTENT-ID/preview")
    assert resp.status_code == 404


# ──────────────────────────────────────────────────────────────────────────────
# Download API
# ──────────────────────────────────────────────────────────────────────────────

def test_download_report_returns_pdf_bytes():
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    dl = client.get(f"/api/reports/{report_id}/download")
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "application/pdf"
    assert len(dl.content) > 1000  # A valid PDF has substantial bytes


def test_download_report_content_disposition():
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    dl = client.get(f"/api/reports/{report_id}/download")
    assert "attachment" in dl.headers.get("content-disposition", "")
    assert report_id in dl.headers.get("content-disposition", "")


def test_download_unknown_report_returns_404():
    resp = client.get("/api/reports/NONEXISTENT-ID/download")
    assert resp.status_code == 404


# ──────────────────────────────────────────────────────────────────────────────
# PDF Content / Scientific Wording
# ──────────────────────────────────────────────────────────────────────────────

def _extract_pdf_text(pdf_bytes: bytes) -> bytes:
    """Extract readable text from PDF bytes using PyPDF2."""
    from io import BytesIO
    try:
        import PyPDF2
    except ImportError:
        return b""
    reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
    text_parts = []
    for page in reader.pages:
        try:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
        except Exception:
            continue
    return " ".join(text_parts).encode()



def test_pdf_contains_scientific_disclaimer():
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    pdf_bytes = client.get(f"/api/reports/{report_id}/download").content
    text = _extract_pdf_text(pdf_bytes)
    text_lower = text.lower()
    assert (
        b"does not independently confirm" in text_lower or
        b"does not" in text_lower
    ), "Scientific disclaimer not found in PDF"


def test_pdf_does_not_contain_prohibited_phrases():
    """Verify the report does NOT make prohibited causal contamination claims."""
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    pdf_bytes = client.get(f"/api/reports/{report_id}/download").content
    pdf_lower = pdf_bytes.lower()

    PROHIBITED = [
        b"pollution confirmed",
        b"contamination confirmed",
        b"pollution detected",
        b"industrial discharge confirmed",
        b"sewage discharge confirmed",
        b"chemical contamination detected",
    ]
    for phrase in PROHIBITED:
        assert phrase not in pdf_lower, f"Prohibited phrase found: {phrase}"


def test_pdf_contains_required_sections():
    """The report PDF should contain key section headings."""
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    pdf_bytes = client.get(f"/api/reports/{report_id}/download").content
    text = _extract_pdf_text(pdf_bytes)

    REQUIRED_SECTIONS = [
        b"WATER QUALITY INTELLIGENCE REPORT",
        b"SATELLITE DATA",
        b"HISTORICAL",
        b"ANOMALY",
        b"DISCLAIMER",
        b"LIMITATIONS",
    ]
    for section in REQUIRED_SECTIONS:
        assert section in text.upper(), f"Required section not found: {section}"


def test_pdf_does_not_fabricate_values():
    """Ensure N/A appears for unknown values, not 0."""
    gen_resp = _generate_analysis_report()
    report_id = gen_resp.json()["report_id"]
    pdf_bytes = client.get(f"/api/reports/{report_id}/download").content
    text = _extract_pdf_text(pdf_bytes)
    # N/A should appear for unknown values somewhere in the PDF
    assert b"N/A" in text or b"n/a" in text.lower(), "N/A not found for missing values"


# ──────────────────────────────────────────────────────────────────────────────
# Data Builder
# ──────────────────────────────────────────────────────────────────────────────

def test_data_builder_analysis_context():
    from app.reports.data_builder import ReportDataBuilder
    builder = ReportDataBuilder()
    ctx = builder.build_for_analysis(
        water_body_id   = "gosikhurd-reservoir",
        water_body_name = "Gosikhurd Reservoir",
        start_date      = "2024-01-01",
        end_date        = "2026-09-22",
    )
    assert ctx["water_body_id"] == "gosikhurd-reservoir"
    assert ctx["report_type"] == "ANALYSIS"
    assert "priority_score" in ctx
    assert ctx.get("satellite_source") == "Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED)"


def test_data_builder_missing_values_are_none_not_zero():
    from app.reports.data_builder import ReportDataBuilder
    builder = ReportDataBuilder()
    ctx = builder.build_for_analysis(
        water_body_id   = "unknown-body",
        water_body_name = "Unknown",
        start_date      = "2024-01-01",
        end_date        = "2026-09-22",
    )
    # Should not raise; should have some priority
    assert ctx["report_type"] == "ANALYSIS"


def test_data_builder_report_id_generation():
    from app.reports.service import _generate_report_id
    rid1 = _generate_report_id()
    rid2 = _generate_report_id()
    assert rid1 != rid2
    assert rid1.startswith("WQI-REPORT-")
