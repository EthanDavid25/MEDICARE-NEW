"""
MEDICARE Doctor Handover PDF Summary Generator.
Generates a structured, professional clinical summary PDF using ReportLab.
Works 100% offline without requiring internet connectivity or external APIs.
"""
from pathlib import Path
from datetime import datetime
import json
import logging

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

logger = logging.getLogger("medicare.reports")

def generate_doctor_handover_pdf(
    patient: dict,
    assessment: dict,
    output_path: Path | str
) -> str:
    """
    Builds a professional clinical handover summary PDF.
    Returns the absolute path to the generated PDF.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0A2342")   # Navy Blue
    secondary_color = colors.HexColor("#0D6EFD") # Med Blue
    urgent_red = colors.HexColor("#DC3545")
    caution_amber = colors.HexColor("#FD7E14")
    safe_green = colors.HexColor("#198754")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#222222")
    )
    bold_body = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold"
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#777777")
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("MEDICARE — CLINICAL HANDOVER SUMMARY", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"Session Ref: {assessment.get('session_id', 'N/A')} | "
        f"Engine: v{assessment.get('triage_version', '1.0.0')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 2. Patient Demographics Block
    p_name = patient.get("display_name", "Anonymous")
    dob = patient.get("date_of_birth", "Not recorded")
    sex = (patient.get("biological_sex", "Not recorded") or "").replace("_", " ").title()
    blood = patient.get("blood_group", "Unknown")
    allergies = patient.get("known_allergies", "None documented")
    meds = patient.get("current_medications", "None documented")
    hx = patient.get("chronic_conditions", "None documented")
    emerg_contact = patient.get("emergency_contact", "Not provided")

    pt_data = [
        [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(p_name, bold_body),
         Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(dob, body_style)],
        [Paragraph("<b>Biological Sex:</b>", body_style), Paragraph(sex, body_style),
         Paragraph("<b>Blood Group:</b>", body_style), Paragraph(blood, body_style)],
        [Paragraph("<b>Known Allergies:</b>", body_style), Paragraph(allergies, body_style),
         Paragraph("<b>Emergency Contact:</b>", body_style), Paragraph(emerg_contact, body_style)],
        [Paragraph("<b>Current Medications:</b>", body_style), Paragraph(meds, body_style),
         Paragraph("<b>Medical History:</b>", body_style), Paragraph(hx, body_style)]
    ]
    t_patient = Table(pt_data, colWidths=[100, 170, 100, 170])
    t_patient.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EEEEEE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(Paragraph("1. PATIENT DEMOGRAPHICS & BACKGROUND", section_heading))
    story.append(t_patient)
    story.append(Spacer(1, 8))

    # 3. Triage Classification Banner
    cat = assessment.get("urgency_category", 3)
    cat_label = assessment.get("urgency_label", "Routine Healthcare")
    if cat == 1:
        cat_bg = colors.HexColor("#F8D7DA")
        cat_border = urgent_red
        cat_text_color = urgent_red
    elif cat == 2:
        cat_bg = colors.HexColor("#FFF3CD")
        cat_border = caution_amber
        cat_text_color = caution_amber
    elif cat == 3:
        cat_bg = colors.HexColor("#D1E7DD")
        cat_border = safe_green
        cat_text_color = safe_green
    else:
        cat_bg = colors.HexColor("#E2E3E5")
        cat_border = colors.HexColor("#6C757D")
        cat_text_color = colors.HexColor("#6C757D")

    triage_banner_data = [
        [
            Paragraph(f"<b>TRIAGE CLASSIFICATION: CATEGORY {cat} — {cat_label.upper()}</b>", ParagraphStyle(
                "TriageBanner",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=16,
                textColor=cat_text_color
            )),
            Paragraph(f"<b>Evaluation Time:</b> {assessment.get('completed_at', 'N/A')}", body_style)
        ]
    ]
    t_banner = Table(triage_banner_data, colWidths=[360, 180])
    t_banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cat_bg),
        ("BOX", (0, 0), (-1, -1), 1.5, cat_border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(Paragraph("2. PRELIMINARY TRIAGE OUTCOME", section_heading))
    story.append(t_banner)
    story.append(Spacer(1, 8))

    # 4. Reported Chief Symptoms
    symptoms = assessment.get("symptoms", [])
    if isinstance(symptoms, str):
        try:
            symptoms = json.loads(symptoms)
        except Exception:
            symptoms = []

    sym_rows = [
        [Paragraph("<b>Symptom</b>", bold_body),
         Paragraph("<b>Severity (1-10)</b>", bold_body),
         Paragraph("<b>Duration</b>", bold_body),
         Paragraph("<b>Trajectory</b>", bold_body),
         Paragraph("<b>Warning Flag</b>", bold_body)]
    ]
    for s in symptoms:
        sym_name = s.get("symptom_name") or s.get("name") or s.get("symptom_code", "Unknown")
        sev = f"{s.get('severity', 'N/A')} / 10"
        dur = f"{s.get('duration_value', '')} {s.get('duration_unit', '')}".strip() or "N/A"
        prog = (s.get("progression") or "unchanged").title()
        is_warn = "YES - RED FLAG" if (s.get("is_emergency_flag") or s.get("is_emergency_warning")) else "No"
        warn_style = ParagraphStyle("W", parent=body_style, textColor=urgent_red if "YES" in is_warn else colors.black)
        
        sym_rows.append([
            Paragraph(sym_name, body_style),
            Paragraph(sev, body_style),
            Paragraph(dur, body_style),
            Paragraph(prog, body_style),
            Paragraph(is_warn, warn_style)
        ])

    t_sym = Table(sym_rows, colWidths=[160, 90, 90, 100, 100])
    t_sym.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EAEAEA")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(Paragraph("3. REPORTED SYMPTOMS & CLINICAL PARAMETERS", section_heading))
    story.append(t_sym)
    story.append(Spacer(1, 8))

    # 5. Rationale & Triggered Warning Signs
    story.append(Paragraph("4. CLINICAL RATIONALE & TRIGGERED INDICATORS", section_heading))
    explanation = assessment.get("explanation") or assessment.get("summary_explanation", "No explanation recorded.")
    story.append(Paragraph(f"<b>Summary:</b> {explanation}", body_style))
    story.append(Spacer(1, 4))

    # Severity Score and Trajectory
    sev_score = assessment.get("severity_score", 0.0)
    prog_trend = assessment.get("progression_trend", "unknown")
    try:
        sev_display = f"{float(sev_score):.1f} / 10.0"
    except (ValueError, TypeError):
        sev_display = str(sev_score)
    story.append(Paragraph(
        f"<b>Computed Severity Metric:</b> {sev_display} &nbsp;|&nbsp; "
        f"<b>Progression Trajectory:</b> {str(prog_trend).title()}",
        body_style
    ))
    story.append(Spacer(1, 4))

    warnings = assessment.get("warnings_found") or assessment.get("warning_signs_found", [])
    if isinstance(warnings, str):
        try:
            warnings = json.loads(warnings)
        except Exception:
            warnings = []
    if warnings:
        story.append(Paragraph("<b>Warning Signs & Emergency Indicators:</b>", bold_body))
        for w in warnings:
            story.append(Paragraph(f"• <font color='#DC3545'>{w}</font>", body_style))
        story.append(Spacer(1, 4))

    # Triggered Clinical Rules (with technical IDs)
    rules = assessment.get("rules_triggered", [])
    if isinstance(rules, str):
        try:
            rules = json.loads(rules)
        except Exception:
            rules = []
    if rules:
        story.append(Paragraph("<b>Triggered Clinical Rules (Technical IDs):</b>", bold_body))
        for r in rules:
            if isinstance(r, dict):
                rid = r.get("rule_id", "RULE")
                desc = r.get("explanation") or r.get("description", "")
                r_text = f"[{rid}] {desc}" if desc else f"[{rid}]"
            else:
                r_text = str(r)
            story.append(Paragraph(f"• {r_text}", body_style))
        story.append(Spacer(1, 4))

    # Unanswered Safety Questions / Incomplete Clinical Data Points
    missing = assessment.get("missing_critical_data", [])
    if isinstance(missing, str):
        try:
            missing = json.loads(missing)
        except Exception:
            missing = []
    if missing:
        story.append(Paragraph("<b>Unanswered Safety Questions / Incomplete Clinical Data:</b>", bold_body))
        for m in missing:
            story.append(Paragraph(f"• <font color='#B45309'>{m}</font>", body_style))
        story.append(Spacer(1, 4))

    # Recommended Clinical Next Steps
    steps = assessment.get("recommended_next_steps", [])
    if isinstance(steps, str):
        try:
            steps = json.loads(steps)
        except Exception:
            steps = []
    if steps:
        story.append(Paragraph("<b>Recommended Clinical Next Steps:</b>", bold_body))
        for s in steps:
            story.append(Paragraph(f"• {s}", body_style))
        story.append(Spacer(1, 4))

    # 6. Mandatory Governance & Disclaimer Box
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=6))
    story.append(Paragraph(
        "<b>CLINICAL DISCLAIMER & NOTICE TO PHYSICIAN:</b> This summary is produced by MEDICARE, an offline-first "
        "medical symptoms triage advisor. This document is intended solely to facilitate structured handover communication "
        "between the patient and an attending medical professional. It does NOT constitute a confirmed medical diagnosis, "
        "treatment plan, or prognosis. The attending physician must exercise independent clinical judgment and perform "
        "appropriate diagnostic verification.",
        disclaimer_style
    ))

    # Build document
    doc.build(story)
    logger.info("Doctor Handover PDF successfully generated at: %s", output_file)
    return str(output_file)
