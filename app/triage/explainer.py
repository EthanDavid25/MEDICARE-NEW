"""
MEDICARE Explainable Triage Reasoning Engine.
Generates plain-language, transparent clinical rationales for triage decisions,
outlining why a category was reached, warning signs, limitations, and next steps.
"""
from typing import Any

URGENCY_TITLES = {
    1: "Category 1 — Emergency Care",
    2: "Category 2 — Early Medical Consultation",
    3: "Category 3 — Routine Healthcare Guidance",
    4: "Category 4 — Insufficient Information"
}

DISCLAIMER_TEXT = (
    "MEDICARE is a preliminary medical symptom assessment and navigation tool. "
    "It does NOT diagnose medical conditions, prescribe treatments or medications, "
    "or replace evaluation by a qualified medical professional. If you experience severe, "
    "rapidly worsening, or distressing symptoms, contact emergency services without delay."
)

def build_explanation(
    urgency_category: int,
    symptoms: list[dict],
    followup_answers: dict[str, str],
    rules_triggered: list[dict],
    warning_signs_found: list[str],
    contradictions: list[str],
    missing_data: list[str],
    progression_trend: str,
    severity_score: float
) -> tuple[str, list[str], list[str], str, str]:
    """
    Returns:
    (summary_explanation, detailed_reasoning, recommended_next_steps, uncertainty_statement, clinical_limitations)
    """
    reasons = []
    next_steps = []
    
    # 1. Summary Explanation
    if urgency_category == 1:
        summary = (
            "EMERGENCY CARE RECOMMENDED: Critical red-flag indicators or severe clinical "
            "warning signs have been identified that require urgent, professional emergency medical evaluation."
        )
    elif urgency_category == 2:
        summary = (
            "EARLY MEDICAL CONSULTATION RECOMMENDED: The reported symptoms, severity trajectory, "
            "or risk profile indicate that timely assessment by a healthcare professional is appropriate within 24 to 48 hours."
        )
    elif urgency_category == 3:
        summary = (
            "ROUTINE HEALTHCARE GUIDANCE: Based on the information provided, there are no immediate "
            "emergency warning signs detected. Routine primary care or guided self-care is indicated."
        )
    else: # Category 4
        summary = (
            "INSUFFICIENT INFORMATION TO CLASSIFY: The answers provided are incomplete, contradictory, "
            "or inadequate to safely assign an urgency classification."
        )

    # 2. Detailed Reasoning
    if warning_signs_found:
        for ws in warning_signs_found:
            reasons.append(f"• Emergency Warning Identified: {ws}")

    if rules_triggered:
        for r in rules_triggered:
            rid = r.get("rule_id", "RULE")
            expl = r.get("explanation", r.get("description", ""))
            reasons.append(f"• Triggered Clinical Rule [{rid}]: {expl}")

    if contradictions:
        for c in contradictions:
            reasons.append(f"• Input Discordance / Contradiction: {c}")

    if missing_data:
        for m in missing_data:
            reasons.append(f"• Incomplete Data Point: {m}")

    reasons.append(f"• Computed Severity Metric: {severity_score:.1f} / 10.0 (Weighted Average)")
    reasons.append(f"• Symptom Progression Trend: {progression_trend.upper()}")

    # 3. Recommended Next Steps
    if urgency_category == 1:
        next_steps.append("1. Call emergency services (e.g. 911 / 112 / 999) or attend the nearest Emergency Department immediately.")
        next_steps.append("2. Do not drive yourself to the hospital; await an ambulance or have someone drive you.")
        next_steps.append("3. Rest in a safe, comfortable position while awaiting medical personnel.")
        next_steps.append("4. Prepare a list of your current medications and health conditions for the attending team.")
    elif urgency_category == 2:
        next_steps.append("1. Contact your general practitioner, family doctor, or visit a local walk-in Urgent Care center today or tomorrow.")
        next_steps.append("2. If your symptoms worsen rapidly or you develop new chest pain, severe shortness of breath, or confusion, upgrade to Emergency Care immediately.")
        next_steps.append("3. Rest, stay hydrated, and monitor your vital signs or symptom severity regularly.")
    elif urgency_category == 3:
        next_steps.append("1. Continue rest and supportive home care measures as appropriate.")
        next_steps.append("2. Schedule a standard routine appointment with your primary care clinic if symptoms persist beyond 5-7 days.")
        next_steps.append("3. Re-run an assessment if symptoms worsen or new concerning signs arise.")
    else: # Category 4
        next_steps.append("1. Review your responses to ensure all required questions are answered accurately.")
        next_steps.append("2. If you are experiencing concerning symptoms, do not assume safety — contact a healthcare provider or telephone helpline (e.g. NHS 111).")
        next_steps.append("3. Conduct a new assessment with full information.")

    # 4. Uncertainty statement
    if urgency_category == 4:
        uncertainty = (
            "HIGH UNCERTAINTY: Due to contradictory responses or omitted critical questions, "
            "this algorithm cannot determine clinical risk. Missing information must never be interpreted as clinical safety."
        )
    elif urgency_category == 1:
        uncertainty = (
            "LOW THRESHOLD FOR ACTION: Because emergency signs can represent life-threatening acute "
            "pathology, this system applies a safety-override principle. False positives are prioritized over missed emergencies."
        )
    else:
        uncertainty = (
            "MODERATE UNCERTAINTY: This assessment is based solely on self-reported inputs without physical "
            "examination, diagnostic imaging, or laboratory data. Symptoms may change rapidly."
        )

    clinical_limitations = DISCLAIMER_TEXT

    return summary, reasons, next_steps, uncertainty, clinical_limitations
