"""
ReportGenerator
---------------
Produces a professional, multi-section PDF report using ReportLab Platypus.
All scientific wording complies with the Prompt 12 specification:
  - "Potential Water Quality Anomaly"
  - "Satellite-observable signals"
  - Never claims confirmed contamination/pollution.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BRAND_BLUE   = colors.HexColor("#1d4ed8")
BRAND_LIGHT  = colors.HexColor("#dbeafe")
SLATE_50     = colors.HexColor("#f8fafc")
SLATE_200    = colors.HexColor("#e2e8f0")
SLATE_700    = colors.HexColor("#334155")
AMBER_400    = colors.HexColor("#fbbf24")
RED_500      = colors.HexColor("#ef4444")
GREEN_600    = colors.HexColor("#16a34a")

DISCLAIMER = (
    "IMPORTANT SCIENTIFIC NOTE: This report identifies changes in "
    "satellite-observable water-quality-related spectral indicators. "
    "It does NOT independently confirm pollution or contamination, determine "
    "pollutant concentrations, or identify a pollution source. Results should be "
    "treated as decision-support evidence and validated through appropriate field "
    "and laboratory investigation."
)


def _na(v: Any) -> str:
    if v is None:
        return "N/A"
    return str(v)


def _score_str(v: Any) -> str:
    if v is None:
        return "N/A"
    try:
        return f"{float(v):.0f}"
    except Exception:
        return str(v)


def _conf_str(v: Any) -> str:
    if v is None:
        return "N/A"
    try:
        return f"{float(v):.0f}%"
    except Exception:
        return str(v)


# ---------------------------------------------------------------------------
# Style factory
# ---------------------------------------------------------------------------

def _make_styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("H1", parent=base["Heading1"],
                              fontSize=18, textColor=BRAND_BLUE,
                              spaceAfter=4, fontName="Helvetica-Bold"),
        "h2": ParagraphStyle("H2", parent=base["Heading2"],
                              fontSize=13, textColor=BRAND_BLUE,
                              spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold"),
        "h3": ParagraphStyle("H3", parent=base["Heading3"],
                              fontSize=10, textColor=SLATE_700,
                              spaceBefore=6, spaceAfter=2, fontName="Helvetica-Bold"),
        "body": ParagraphStyle("Body", parent=base["Normal"],
                                fontSize=9, textColor=SLATE_700,
                                spaceAfter=3, fontName="Helvetica"),
        "small": ParagraphStyle("Small", parent=base["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#64748b"),
                                 spaceAfter=2, fontName="Helvetica"),
        "center": ParagraphStyle("Center", parent=base["Normal"],
                                  fontSize=9, alignment=TA_CENTER,
                                  fontName="Helvetica"),
        "disclaimer": ParagraphStyle("Disc", parent=base["Normal"],
                                      fontSize=8, textColor=SLATE_700,
                                      backColor=colors.HexColor("#fef9c3"),
                                      borderPad=4, spaceAfter=6,
                                      fontName="Helvetica-Oblique"),
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Normal"],
                                       fontSize=22, textColor=colors.white,
                                       alignment=TA_CENTER, fontName="Helvetica-Bold",
                                       spaceAfter=6),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Normal"],
                                     fontSize=11, textColor=colors.HexColor("#bfdbfe"),
                                     alignment=TA_CENTER, fontName="Helvetica"),
        "cover_body": ParagraphStyle("CoverBody", parent=base["Normal"],
                                      fontSize=9, textColor=colors.white,
                                      alignment=TA_CENTER, fontName="Helvetica"),
        "label": ParagraphStyle("Label", parent=base["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#6b7280"),
                                 fontName="Helvetica"),
        "value": ParagraphStyle("Value", parent=base["Normal"],
                                 fontSize=9, textColor=SLATE_700,
                                 fontName="Helvetica-Bold"),
    }


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

class _PageCanvas:
    """Mixin used by SimpleDocTemplate's onPage callback to draw header/footer."""

    def __init__(self, report_id: str, generated_at: str):
        self.report_id    = report_id
        self.generated_at = generated_at

    def on_first_page(self, canvas, doc):
        pass  # Cover page has its own styling

    def on_later_pages(self, canvas, doc):
        W, H = A4
        canvas.saveState()

        # --- Header line ---
        canvas.setFillColor(BRAND_BLUE)
        canvas.rect(0, H - 18*mm, W, 10*mm, fill=1, stroke=0)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.white)
        canvas.drawString(10*mm, H - 11*mm,
                          "SATELLITE-BASED WATER QUALITY & CONTAMINATION INTELLIGENCE")
        canvas.drawRightString(W - 10*mm, H - 11*mm, "Decision Support — Ground/Lab Validation Required")

        # --- Footer ---
        canvas.setStrokeColor(SLATE_200)
        canvas.line(10*mm, 12*mm, W - 10*mm, 12*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(10*mm, 8*mm, f"Report ID: {self.report_id}   |   Generated: {self.generated_at}")
        canvas.drawRightString(W - 10*mm, 8*mm, f"Page {doc.page}")

        canvas.restoreState()


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Assembles a ReportLab Platypus PDF from a ReportDataBuilder context dict."""

    def generate(self, ctx: Dict[str, Any], report_id: str) -> bytes:
        """Return the raw PDF bytes."""
        styles       = _make_styles()
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        pager        = _PageCanvas(report_id, generated_at)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize     = A4,
            rightMargin  = 18*mm,
            leftMargin   = 18*mm,
            topMargin    = 25*mm,
            bottomMargin = 20*mm,
            title        = f"Water Quality Intelligence Report – {report_id}",
            author       = "Satellite-Based Water Quality Intelligence System",
        )

        story: List[Any] = []

        story += self._cover_page(ctx, styles, report_id, generated_at)
        story += self._water_body_section(ctx, styles)
        story += self._satellite_section(ctx, styles)
        story += self._water_detection_section(ctx, styles)
        story += self._spectral_indicators_section(ctx, styles)
        story += self._historical_section(ctx, styles)
        story += self._anomaly_section(ctx, styles)
        story += self._explainability_section(ctx, styles)
        story += self._alert_section(ctx, styles)
        story += self._validation_section(ctx, styles)
        story += self._limitations_section(ctx, styles)
        story += self._disclaimer_section(ctx, styles)

        doc.build(
            story,
            onFirstPage = pager.on_first_page,
            onLaterPages= pager.on_later_pages,
        )

        return buf.getvalue()

    # ------------------------------------------------------------------
    # Cover Page
    # ------------------------------------------------------------------
    def _cover_page(self, ctx, S, report_id, generated_at) -> List[Any]:
        W, _H = A4
        content_w = W - 36*mm

        # Blue cover table
        cover_rows = [
            [Paragraph("WATER QUALITY INTELLIGENCE REPORT", S["cover_title"])],
            [Paragraph("Satellite-Based Water Quality & Contamination Intelligence", S["cover_sub"])],
            [Paragraph("Decision Support — Not a Confirmation of Contamination", S["cover_body"])],
        ]
        cover_tbl = Table(cover_rows, colWidths=[content_w])
        cover_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), BRAND_BLUE),
            ("TEXTCOLOR",     (0,0), (-1,-1), colors.white),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("ROUNDEDCORNERS",(0,0), (-1,-1), [4, 4, 4, 4]),
        ]))

        # KV table
        score     = _score_str(ctx.get("priority_score"))
        band      = _na(ctx.get("priority_band"))
        sev       = _na(ctx.get("severity"))
        conf      = _conf_str(ctx.get("confidence"))
        driver    = _na(ctx.get("primary_driver"))
        rtype     = ctx.get("report_type", "ANALYSIS")
        mode      = ctx.get("processing_mode", "DEMO DATA")
        anomaly   = "YES" if ctx.get("priority_score") and float(ctx.get("priority_score", 0)) >= 40 else "Insufficient Evidence"

        kv = [
            ["Report ID",        report_id],
            ["Report Type",      f"{rtype.title()} Report"],
            ["Water Body",       _na(ctx.get("water_body_name"))],
            ["Analysis Date",    _na(ctx.get("analysis_date"))],
            ["Generated At",     generated_at],
            ["Satellite Source", "Sentinel-2"],
            ["Processing Mode",  mode],
            ["Potential Anomaly",anomaly],
            ["Priority Score",   f"{score} / 100   Band: {band}"],
            ["Severity",         sev],
            ["Confidence",       conf],
            ["Primary Indicator",driver],
        ]

        kv_rows = [
            [Paragraph(k, S["label"]), Paragraph(v, S["value"])]
            for k, v in kv
        ]
        kv_tbl = Table(kv_rows, colWidths=[55*mm, content_w - 55*mm])
        kv_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1), SLATE_50),
            ("TEXTCOLOR",     (0,0), (-1,-1), SLATE_700),
            ("GRID",          (0,0), (-1,-1), 0.3, SLATE_200),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))

        return [
            cover_tbl,
            Spacer(1, 8*mm),
            Paragraph("REPORT METADATA", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            kv_tbl,
            Spacer(1, 8*mm),
            Paragraph("EXECUTIVE SUMMARY", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            Paragraph(
                _na(ctx.get("exec_summary")),
                S["body"],
            ),
            Spacer(1, 4*mm),
            Paragraph(
                f"<b>Recommended Action:</b> {_na(ctx.get('primary_reason'))}",
                S["body"],
            ),
            PageBreak(),
        ]

    # ------------------------------------------------------------------
    # Water Body & AOI
    # ------------------------------------------------------------------
    def _water_body_section(self, ctx, S) -> List[Any]:
        kv = [
            ["Water Body Name",  _na(ctx.get("water_body_name"))],
            ["Water Body ID",    _na(ctx.get("water_body_id"))],
            ["Water Body Type",  _na(ctx.get("water_body_type"))],
            ["Location",         _na(ctx.get("water_body_state"))],
            ["Analysis Date",    _na(ctx.get("analysis_date"))],
            ["Date Range",       f"{_na(ctx.get('start_date'))} → {_na(ctx.get('end_date'))}"],
        ]
        return self._kv_section("WATER BODY & AOI INFORMATION", kv, S)

    # ------------------------------------------------------------------
    # Satellite & Data Quality
    # ------------------------------------------------------------------
    def _satellite_section(self, ctx, S) -> List[Any]:
        kv = [
            ["Satellite",            "Sentinel-2 (ESA Copernicus)"],
            ["Collection",           "COPERNICUS/S2_SR_HARMONIZED"],
            ["Scene ID",             _na(ctx.get("scene_id"))],
            ["Acquisition Date",     _na(ctx.get("acquisition_date"))],
            ["Processing Mode",      _na(ctx.get("processing_mode"))],
            ["Cloud Percentage",     _na(ctx.get("cloud_pct"))],
            ["Valid Pixel %",        _na(ctx.get("valid_pct"))],
            ["Observation Quality",  _na(ctx.get("obs_quality"))],
        ]
        return self._kv_section("SATELLITE DATA & DATA QUALITY", kv, S)

    # ------------------------------------------------------------------
    # Water Detection
    # ------------------------------------------------------------------
    def _water_detection_section(self, ctx, S) -> List[Any]:
        kv = [
            ["Detection Method",        _na(ctx.get("water_detection_method"))],
            ["NDWI Threshold",          "≥ 0.0 (NDWI-based composite)"],
            ["MNDWI Threshold",         "≥ 0.0 (MNDWI-based composite)"],
            ["Detected Water Area",     _na(ctx.get("detected_water_area"))],
            ["Water Coverage",          _na(ctx.get("water_coverage_pct"))],
        ]
        note = Paragraph(
            "The detected water region represents the water extent identified from the current "
            "satellite observation. Changes in water area do not in themselves indicate contamination.",
            S["small"],
        )
        return self._kv_section("WATER DETECTION", kv, S, extra=[note])

    # ------------------------------------------------------------------
    # Spectral Indicators
    # ------------------------------------------------------------------
    def _spectral_indicators_section(self, ctx, S) -> List[Any]:
        rows = ctx.get("indicator_rows", [])
        content = [
            Paragraph("SPECTRAL INDICATORS", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            Paragraph(
                "Satellite-derived spectral indicators are indirect proxy measurements of water-quality-related "
                "optical properties. They represent observable spectral characteristics, NOT direct laboratory measurements.",
                S["body"],
            ),
            Spacer(1, 3*mm),
        ]
        if rows:
            header = ["Indicator", "Current", "Baseline", "Abs. Dev.", "Rel. Dev. %", "Robust Dev.", "Direction", "Contribution"]
            table_data = [header] + [
                [
                    r.get("name", "N/A"),
                    r.get("current", "N/A"),
                    r.get("baseline", "N/A"),
                    r.get("abs_dev", "N/A"),
                    r.get("rel_dev_pct", "N/A"),
                    r.get("robust_dev", "N/A"),
                    r.get("direction", "N/A"),
                    r.get("contribution", "N/A"),
                ]
                for r in rows
            ]
            W, _ = A4
            cw = [(W - 36*mm) / 8] * 8
            tbl = Table(table_data, colWidths=cw)
            tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), BRAND_BLUE),
                ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
                ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0), (-1,-1), 7),
                ("GRID",          (0,0), (-1,-1), 0.3, SLATE_200),
                ("TOPPADDING",    (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("LEFTPADDING",   (0,0), (-1,-1), 3),
                ("BACKGROUND",    (0,1), (-1,-1), SLATE_50),
                ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, SLATE_50]),
            ]))
            content.append(tbl)
        else:
            content.append(Paragraph("Indicator details not available for this report context.", S["small"]))

        content += [Spacer(1, 4*mm)]
        # Interpretation note
        interp = [
            ("NDTI",                     "Turbidity-related spectral signal. Elevated values may indicate increased suspended particles."),
            ("Suspended Sediment Proxy", "Satellite-derived spectral signal associated with suspended particles."),
            ("NDCI",                     "Chlorophyll-related spectral indicator. Elevated values may indicate phytoplankton activity."),
            ("FAI",                      "Algal-activity-related spectral indicator. Elevated values may suggest floating algal material."),
        ]
        for name, desc in interp:
            content.append(Paragraph(f"<b>{name}:</b> {desc}", S["small"]))

        content.append(PageBreak())
        return content

    # ------------------------------------------------------------------
    # Historical Analysis
    # ------------------------------------------------------------------
    def _historical_section(self, ctx, S) -> List[Any]:
        obs   = ctx.get("hist_obs_count", 0)
        start = _na(ctx.get("hist_start"))
        end   = _na(ctx.get("hist_end"))
        ts    = ctx.get("time_series", [])
        baseline = ctx.get("hist_baseline", {})

        content = [
            Paragraph("HISTORICAL BASELINE & TIME-SERIES", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
        ]

        kv = [
            ["Historical Period",    f"{start} → {end}"],
            ["Observations",         str(obs)],
            ["Baseline Method",      "Seasonal Median (per month-of-year)"],
            ["Deviation Metric",     "Median Absolute Deviation (MAD)"],
        ]
        for k, v in kv:
            content.append(Paragraph(f"<b>{k}:</b> {v}", S["body"]))

        content += [Spacer(1, 3*mm)]

        # Baseline table
        if baseline:
            LABELS = {
                "ndti":                     "NDTI",
                "suspended_sediment_proxy": "Suspended Sediment",
                "ndci":                     "NDCI",
                "fai":                      "FAI",
            }
            b_header = ["Indicator", "Baseline Median", "MAD"]
            b_rows   = [b_header]
            for key, label in LABELS.items():
                b = baseline.get(key, {})
                if not b:
                    continue
                b_rows.append([
                    label,
                    f"{b.get('median', 'N/A'):.4f}" if isinstance(b.get("median"), float) else "N/A",
                    f"{b.get('mad', 'N/A'):.4f}"    if isinstance(b.get("mad"),    float) else "N/A",
                ])
            if len(b_rows) > 1:
                W, _ = A4
                tbl = Table(b_rows, colWidths=[(W-36*mm)/3]*3)
                tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0), (-1,0), BRAND_BLUE),
                    ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
                    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE",      (0,0), (-1,-1), 8),
                    ("GRID",          (0,0), (-1,-1), 0.3, SLATE_200),
                    ("TOPPADDING",    (0,0), (-1,-1), 3),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                    ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, SLATE_50]),
                ]))
                content.append(tbl)

        # Recent time-series table (last 12)
        if ts:
            content += [Spacer(1, 4*mm), Paragraph("Recent Time-Series Observations (last 12)", S["h3"])]
            ts_header = ["Date", "NDTI", "Susp. Sed.", "NDCI", "FAI"]
            ts_rows = [ts_header]
            for row in ts[-12:]:
                ts_rows.append([
                    row.get("date", "N/A"),
                    _na(row.get("ndti")),
                    _na(row.get("susp_sed")),
                    _na(row.get("ndci")),
                    _na(row.get("fai")),
                ])
            W, _ = A4
            tbl2 = Table(ts_rows, colWidths=[(W-36*mm)/5]*5)
            tbl2.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), SLATE_700),
                ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
                ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0), (-1,-1), 7),
                ("GRID",          (0,0), (-1,-1), 0.3, SLATE_200),
                ("TOPPADDING",    (0,0), (-1,-1), 2),
                ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, SLATE_50]),
            ]))
            content.append(tbl2)

        content.append(PageBreak())
        return content

    # ------------------------------------------------------------------
    # Anomaly & Evidence
    # ------------------------------------------------------------------
    def _anomaly_section(self, ctx, S) -> List[Any]:
        score = ctx.get("priority_score")
        band  = _na(ctx.get("priority_band"))
        sev   = _na(ctx.get("severity"))
        conf  = _conf_str(ctx.get("confidence"))
        driver= _na(ctx.get("primary_driver"))
        supp  = ctx.get("supporting_inds", [])
        evs   = ctx.get("evidence_stmts", [])

        content = [
            Paragraph("ANOMALY DETECTION & MULTI-INDICATOR EVIDENCE", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
        ]

        kv = [
            ["Investigation Priority Score", f"{_score_str(score)} / 100"],
            ["Priority Band",                band],
            ["Severity",                     sev],
            ["Analytical Confidence",        conf],
            ["Primary Driver",               driver],
            ["Supporting Indicators",        ", ".join(supp) if supp else "N/A"],
        ]
        for k, v in kv:
            content.append(Paragraph(f"<b>{k}:</b> {v}", S["body"]))

        if evs:
            content += [Spacer(1, 3*mm), Paragraph("Evidence Statements", S["h3"])]
            for ev in evs:
                sig  = ev.get("significance", "LOW")
                ind  = ev.get("indicator", "Unknown")
                desc = ev.get("description", "")
                bullet_color = "red" if sig == "HIGH" else ("orange" if sig == "MODERATE" else "goldenrod")
                content.append(Paragraph(
                    f'<font color="{bullet_color}">●</font> <b>[{sig}]</b> <b>{ind}:</b> {desc}',
                    S["body"],
                ))
        else:
            content.append(Paragraph("No detailed evidence statements available.", S["small"]))

        content.append(Spacer(1, 4*mm))
        return content

    # ------------------------------------------------------------------
    # Explainability
    # ------------------------------------------------------------------
    def _explainability_section(self, ctx, S) -> List[Any]:
        summary = _na(ctx.get("exec_summary"))
        reason  = _na(ctx.get("primary_reason"))
        recs    = ctx.get("recommendations", [])

        content = [
            Paragraph("EXPLAINABILITY — WHY WAS THIS ZONE FLAGGED?", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            Paragraph(f"<b>Primary Reason:</b> {reason}", S["body"]),
            Spacer(1, 2*mm),
            Paragraph(f"<b>Summary:</b> {summary}", S["body"]),
            Spacer(1, 3*mm),
        ]

        if recs:
            content.append(Paragraph("Recommended Actions", S["h3"]))
            for rec in recs:
                action  = rec.get("action", "")
                urgency = rec.get("urgency", "")
                content.append(Paragraph(
                    f"<b>[{urgency}]</b> {action}", S["body"]
                ))
        else:
            content.append(Paragraph("No specific recommendations available.", S["small"]))

        content.append(PageBreak())
        return content

    # ------------------------------------------------------------------
    # Alert Information
    # ------------------------------------------------------------------
    def _alert_section(self, ctx, S) -> List[Any]:
        alert_id = ctx.get("alert_id")
        if not alert_id:
            return [
                Paragraph("ALERT INFORMATION", S["h2"]),
                HRFlowable(width="100%", thickness=1, color=SLATE_200),
                Spacer(1, 3*mm),
                Paragraph("No alert was generated for this analysis.", S["body"]),
                Spacer(1, 4*mm),
            ]

        kv = [
            ["Alert ID",             _na(alert_id)],
            ["Investigation Status", _na(ctx.get("alert_status"))],
            ["Analysis Date",        _na(ctx.get("analysis_date"))],
            ["Summary",              _na(ctx.get("alert_summary"))],
        ]
        return self._kv_section("ALERT INFORMATION", kv, S)

    # ------------------------------------------------------------------
    # Ground / Lab Validation
    # ------------------------------------------------------------------
    def _validation_section(self, ctx, S) -> List[Any]:
        return [
            Paragraph("GROUND / LABORATORY VALIDATION", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            Paragraph("<b>Validation Status:</b> Not yet validated", S["body"]),
            Paragraph(
                "Recommended: Collect field observations and laboratory water-quality measurements "
                "for the flagged region and associate them with this report (Report ID above).",
                S["body"],
            ),
            Spacer(1, 4*mm),
        ]

    # ------------------------------------------------------------------
    # Scientific Limitations
    # ------------------------------------------------------------------
    def _limitations_section(self, ctx, S) -> List[Any]:
        items = [
            "Satellite-derived indicators are indirect, proxy measurements of water-quality-related spectral properties.",
            "They represent observable spectral characteristics and are NOT direct laboratory water-quality measurements.",
            "Satellite observations do not independently confirm contamination, pollution, or its source.",
            "Cloud cover, shadows, aerosols, and atmospheric conditions can affect spectral measurements.",
            "Historical baseline quality depends on the number and consistency of available satellite observations.",
            "Ground and laboratory measurements are required for definitive water-quality validation.",
            "This report is intended for investigation prioritisation and decision support, NOT regulatory enforcement.",
            "Absence of a satellite-observable anomaly does not guarantee the absence of contamination.",
        ]
        content = [
            Paragraph("SCIENTIFIC LIMITATIONS", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
        ]
        for i, item in enumerate(items, 1):
            content.append(Paragraph(f"{i}. {item}", S["body"]))
        content.append(Spacer(1, 4*mm))
        return content

    # ------------------------------------------------------------------
    # Disclaimer
    # ------------------------------------------------------------------
    def _disclaimer_section(self, ctx, S) -> List[Any]:
        return [
            Paragraph("DISCLAIMER", S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            Paragraph(DISCLAIMER, S["disclaimer"]),
            Spacer(1, 4*mm),
            Paragraph(
                f"Report generated by the Satellite-Based Water Quality & Contamination Intelligence System. "
                f"This system is for research and decision-support purposes only.",
                S["small"],
            ),
        ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def _kv_section(
        self, title: str, kv: List, S: Dict, extra: Optional[List] = None
    ) -> List[Any]:
        W, _ = A4
        content_w = W - 36*mm
        rows = [
            [Paragraph(k, S["label"]), Paragraph(v, S["value"])]
            for k, v in kv
        ]
        tbl = Table(rows, colWidths=[55*mm, content_w - 55*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1), SLATE_50),
            ("GRID",          (0,0), (-1,-1), 0.3, SLATE_200),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        out = [
            Paragraph(title, S["h2"]),
            HRFlowable(width="100%", thickness=1, color=SLATE_200),
            Spacer(1, 3*mm),
            tbl,
        ]
        if extra:
            out += extra
        out.append(Spacer(1, 5*mm))
        return out
