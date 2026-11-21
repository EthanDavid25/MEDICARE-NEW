"""
Pure Python fallback for triage rule evaluation and emergency overrides.
Mirrors native/src/rule_evaluator.c & native/src/triage_primitives.c
"""
from typing import Any

# Urgency categories: lower number = higher urgency
URGENCY_EMERGENCY = 1
URGENCY_EARLY = 2
URGENCY_ROUTINE = 3
URGENCY_INSUFFICIENT = 4

URGENCY_LABELS = {
    URGENCY_EMERGENCY: "Emergency Care",
    URGENCY_EARLY: "Early Medical Consultation",
    URGENCY_ROUTINE: "Routine Healthcare",
    URGENCY_INSUFFICIENT: "Insufficient Information"
}

def check_emergency_override(symptoms: list[dict], warning_signs: list[dict] = None) -> tuple[bool, list[str]]:
    """
    Checks if any reported symptom carries an immediate emergency flag or triggers a red-flag warning sign.
    Mirrors check_emergency_override() in rule_evaluator.c
    """
    reasons = []
    has_override = False
    
    for s in symptoms:
        if s.get("is_emergency_flag") or s.get("is_emergency_warning"):
            has_override = True
            name = s.get("name") or s.get("symptom_name") or s.get("code")
            reasons.append(f"Emergency warning sign reported: {name}")
    
    return has_override, reasons

def evaluate_single_rule(rule: dict, symptoms: list[dict], followup_answers: dict[str, str], risk_factors: list[str]) -> bool:
    """
    Evaluates conditions of a single triage rule.
    Mirrors evaluate_single_rule() in rule_evaluator.c
    """
    if not rule.get("is_active", True):
        return False
        
    conditions = rule.get("conditions", {})
    if not conditions:
        return False
        
    symptom_codes = {s.get("code") or s.get("symptom_code", "") for s in symptoms}
    max_severity = max([s.get("severity", 0) for s in symptoms], default=0)
    
    # 1. Required symptoms check
    required_syms = conditions.get("required_symptoms", [])
    if required_syms:
        if not any(code in symptom_codes for code in required_syms):
            return False
            
    # 2. Min severity check
    min_sev = conditions.get("min_severity", 0)
    if min_sev > 0 and max_severity < min_sev:
        return False
        
    # 3. Max severity check
    max_sev = conditions.get("max_severity", 10)
    if max_sev < 10 and max_severity > max_sev:
        return False
        
    # 4. Specific followup answers
    req_answers = conditions.get("followup_answers", {})
    for qid, exp_ans in req_answers.items():
        if followup_answers.get(qid) != exp_ans:
            return False
            
    # 5. Any followup answers matching
    any_answers = conditions.get("any_followup_answers", {})
    if any_answers:
        matched_any = any(followup_answers.get(qid) == exp_ans for qid, exp_ans in any_answers.items())
        if not matched_any:
            return False
            
    # 6. Min symptoms count
    min_count = conditions.get("min_symptoms_count", 0)
    if min_count > 0 and len(symptoms) < min_count:
        return False
        
    # 7. Contradiction detected
    if conditions.get("contradiction_detected"):
        return False  # Handled separately by validator
        
    # 8. Missing critical answers
    if conditions.get("missing_critical_answers"):
        return False
        
    return True

def find_highest_urgency(categories: list[int]) -> int:
    """
    Returns the lowest integer category (which corresponds to highest medical urgency).
    Category 1 (Emergency) > Category 2 (Early) > Category 3 (Routine) > Category 4 (Insufficient)
    """
    valid = [c for c in categories if 1 <= c <= 4]
    if not valid:
        return URGENCY_INSUFFICIENT
    return min(valid)
