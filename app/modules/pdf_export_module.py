"""PDF Export Module for Medical Reports.

Generates professional PDF documents with:
- Patient information
- Original report text
- AI-generated simplified summary
- Risk assessment with color coding
- Recommendations
- Multilingual support
- Branding and footer
"""
import io
import logging
from datetime import datetime
from typing import Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)


def _get_risk_color(risk_level: str) -> colors.Color:
    """Get color for risk level badge."""
    color_map = {
        "High": colors.HexColor("#d62728"),  # Red
        "Moderate": colors.HexColor("#ff7f0e"),  # Orange
        "Low": colors.HexColor("#2ca02c"),  # Green
    }
    return color_map.get(risk_level, colors.gray)


def generate_report_pdf(
    report_data: Dict[str, object],
    report_text: str,
    patient_info: Optional[Dict[str, str]] = None,
) -> bytes:
    """Generate PDF report from medical report data.

    Args:
        report_data: Dictionary containing:
            - summary: Simplified explanation
            - risk: Risk assessment dict (risk_level, risk_score, alerts, recommendation)
            - audio_url: URL to audio explanation (optional)
        report_text: Original medical report text
        patient_info: Optional patient metadata (name, age, date, etc.)

    Returns:
        PDF file as bytes
    """
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=30,
        alignment=1,  # Center
        fontName="Helvetica-Bold",
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        textColor=colors.HexColor("#34495e"),
        fontName="Helvetica",
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.gray,
        fontName="Helvetica",
    )

    # ═════════════════════════════════════════════════════════════════════════
    # HEADER
    # ═════════════════════════════════════════════════════════════════════════

    # Title
    elements.append(Paragraph("🏥 Medical Report Analysis", title_style))
    elements.append(Paragraph(
        "AI-Powered Report Interpreter & Health Communication Platform",
        small_style
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # Patient Information (if provided)
    if patient_info:
        patient_data = [
            ["Report ID:", patient_info.get("report_id", "N/A")],
            ["Generated:", patient_info.get("date", datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC"))],
        ]
        if patient_info.get("location"):
            patient_data.append(["Location:", patient_info["location"]])
        if patient_info.get("language"):
            patient_data.append(["Language:", patient_info["language"].upper()])

        patient_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
        patient_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 0.3 * inch))

    # ═════════════════════════════════════════════════════════════════════════
    # RISK ASSESSMENT
    # ═════════════════════════════════════════════════════════════════════════

    risk = report_data.get("risk", {})
    risk_level = risk.get("risk_level", "Unknown")
    risk_score = risk.get("risk_score", 0)
    risk_color = _get_risk_color(risk_level)

    elements.append(Paragraph("Risk Assessment", heading_style))

    # Risk level badge table
    risk_icon = {"High": "🔴", "Moderate": "🟠", "Low": "🟢"}.get(risk_level, "⚪")
    risk_table_data = [
        [f"{risk_icon} {risk_level}", f"Score: {risk_score}"]
    ]
    risk_table = Table(risk_table_data, colWidths=[3 * inch, 3 * inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), risk_color),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Medical Alerts
    alerts = risk.get("alerts", [])
    if alerts:
        elements.append(Paragraph("Medical Alerts", heading_style))
        for alert in alerts:
            elements.append(Paragraph(f"⚠️ {alert}", body_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ═════════════════════════════════════════════════════════════════════════
    # SIMPLIFIED SUMMARY
    # ═════════════════════════════════════════════════════════════════════════

    summary = report_data.get("summary", "No summary available.")
    elements.append(Paragraph("Simplified Explanation", heading_style))
    elements.append(Paragraph(
        "This is an AI-generated summary in simple, patient-friendly language:",
        small_style
    ))
    elements.append(Spacer(1, 0.1 * inch))

    # Summary in a box
    summary_style = ParagraphStyle(
        "SummaryBox",
        parent=body_style,
        fontSize=12,
        leading=18,
        backColor=colors.HexColor("#f0f8ff"),
        borderColor=colors.HexColor("#1f77b4"),
        borderWidth=1.5,
        borderPadding=12,
        borderRadius=5,
    )
    elements.append(Paragraph(summary, summary_style))
    elements.append(Spacer(1, 0.3 * inch))

    # ═════════════════════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ═════════════════════════════════════════════════════════════════════════

    recommendation = risk.get("recommendation", "")
    if recommendation:
        elements.append(Paragraph("Recommendations", heading_style))
        recommendation_style = ParagraphStyle(
            "RecommendationBox",
            parent=body_style,
            fontSize=11,
            leading=16,
            backColor=colors.HexColor("#e8f5e9") if risk_level == "Low" else (
                colors.HexColor("#fff3e0") if risk_level == "Moderate" else colors.HexColor("#ffebee")
            ),
            borderColor=risk_color,
            borderWidth=1.5,
            borderPadding=12,
            borderRadius=5,
        )
        elements.append(Paragraph(f"📋 {recommendation}", recommendation_style))
        elements.append(Spacer(1, 0.3 * inch))

    # ═════════════════════════════════════════════════════════════════════════
    # ORIGINAL REPORT (NEW PAGE)
    # ═════════════════════════════════════════════════════════════════════════

    elements.append(PageBreak())
    elements.append(Paragraph("Original Medical Report",heading_style))
    elements.append(Paragraph(
        "Below is the original medical report text as extracted from your document:",
        small_style
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # Original report text in monospace style
    report_style = ParagraphStyle(
        "ReportText",
        parent=styles["Code"],
        fontSize=9,
        leading=12,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
        textColor=colors.HexColor("#2c3e50"),
        fontName="Courier",
    )

    # Split report into paragraphs to avoid overflow
    report_paragraphs = report_text.split("\n\n")
    for para in report_paragraphs:
        if para.strip():
            # Escape special XML characters
            para_escaped = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.append(Paragraph(para_escaped, report_style))

    # ═════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═════════════════════════════════════════════════════════════════════════

    elements.append(Spacer(1, 0.5 * inch))
    footer_text = f"""
    <para alignment="center">
        <b>Important Medical Disclaimer</b><br/>
        This report was generated by an AI-powered medical report interpreter. The simplified summary and risk
        assessment are provided for informational purposes only and should not replace professional medical advice,
        diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.<br/><br/>
        Generated by: AI Medical Report Interpreter Platform<br/>
        Date: {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")}<br/>
        Platform: https://github.com/medical-report-ai
    </para>
    """
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=small_style,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#7f8c8d"),
        borderColor=colors.HexColor("#bdc3c7"),
        borderWidth=1,
        borderPadding=8,
        alignment=1,  # Center
    )
    elements.append(Paragraph(footer_text, disclaimer_style))

    # Build PDF
    try:
        doc.build(elements)
        logger.info("PDF generated successfully (%d bytes)", buffer.tell())
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.exception("PDF generation failed: %s", e)
        raise
