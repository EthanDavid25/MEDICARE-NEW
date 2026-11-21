"""
Pure Python fallback for input validation and contradiction detection.
Mirrors native/src/data_validator.c
"""
from typing import Any

def validate_symptom_entry(entry: dict) -> tuple[bool, list[str]]:
    """
    Validates code, name, severity (1-10), duration.
    Mirrors validate_symptom_entry() in data_validator.c
    """
    errors = []
    code = entry.get("code") or entry.get("symptom_code", "")
    name = entry.get("name") or entry.get("symptom_name", "")
    
    if not code and not name:
        errors.append("Symptom code or name must not be empty.")
        
    sev = entry.get("severity")
    if sev is not None:
        try:
            val = int(sev)
            if not (1 <= val <= 10):
                errors.append(f"Severity ({val}) must be between 1 and 10.")
        except (ValueError, TypeError):
            errors.append("Severity must be an integer between 1 and 10.")
            
    dur = entry.get("duration_value") or entry.get("duration_hours")
    if dur is not None:
        try:
            val = float(dur)
            if val < 0:
                errors.append("Duration cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Duration must be a positive number.")
            
    return (len(errors) == 0, errors)

def validate_patient_profile(profile: dict) -> tuple[bool, list[str]]:
    """Validates patient demographic data."""
    errors = []
    name = (profile.get("display_name") or "").strip()
    if not name:
        errors.append("Patient display name is required.")
        
    sex = profile.get("biological_sex")
    if sex and sex not in ("male", "female", "other", "prefer_not_to_say"):
        errors.append("Biological sex must be one of: male, female, other, prefer_not_to_say.")
        
    return (len(errors) == 0, errors)

def check_contradictions(symptoms: list[dict], answers: dict[str, str]) -> tuple[bool, list[str]]:
    """
    Detects contradictory responses:
    e.g., Severity = 10 (unbearable) but progression is 'improving' and duration is 'weeks' without distress;
    or emergency symptoms checked as 'NO' in follow-up but present in text.
    Mirrors check_contradictions() in data_validator.c
    """
    contradictions = []
    
    # 1. High severity (>=9) but progression marked as 'improving' with no current limitation
    max_sev = max([s.get("severity", 0) for s in symptoms], default=0)
    prog = answers.get("QID_SYMPTOM_PROGRESSION", "")
    
    if max_sev >= 9 and prog == "IMPROVING":
        # Check if duration is also short
        dur = answers.get("QID_SYMPTOM_DURATION", "")
        if dur == "WEEKS":
            contradictions.append(
                "Discordant report: Extreme severity (9-10/10) reported alongside prolonged chronic duration (>1 week) and actively improving trajectory."
            )
            
    # 2. Chest pain marked with severe shortness of breath, but respiratory difficulty marked as MILD
    symptom_codes = {s.get("code") or s.get("symptom_code", "") for s in symptoms}
    if "SYM_SHORTNESS_OF_BREATH" in symptom_codes and answers.get("QID_RESP_SEVERITY") == "MILD" and max_sev >= 8:
        contradictions.append(
            "Discordant report: Severe overall distress rated, yet breathing difficulty is answered as completely mild."
        )
        
    return (len(contradictions) > 0, contradictions)
