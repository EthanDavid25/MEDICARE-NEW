"""
Pure Python fallback for risk calculation and progression trend detection.
Mirrors native/src/risk_calculator.c
"""

def calculate_severity_score(symptoms: list[dict]) -> float:
    """
    Weighted severity score calculation.
    Emergency flags receive 3x weight; worsening symptoms receive 1.5x weight.
    Mirrors calculate_severity_score() in risk_calculator.c
    """
    if not symptoms:
        return 0.0
        
    weighted_sum = 0.0
    weight_total = 0.0
    
    for s in symptoms:
        severity = float(s.get("severity", 5))
        weight = 1.0
        if s.get("is_emergency_flag") or s.get("is_emergency_warning"):
            weight *= 3.0
        if s.get("progression") == "worsening" or s.get("is_worsening"):
            weight *= 1.5
            
        weighted_sum += severity * weight
        weight_total += weight
        
    return round(weighted_sum / weight_total, 2) if weight_total > 0 else 0.0

def detect_worsening_trend(current_symptoms: list[dict], history: list[dict] = None) -> tuple[float, str]:
    """
    Analyzes progression compared to previous assessments.
    Returns (trend_score: float, trend_label: str)
    Mirrors detect_worsening_trend() in risk_calculator.c
    """
    worsening = 0
    improving = 0
    
    for s in current_symptoms:
        prog = s.get("progression", "").lower()
        if prog == "worsening" or s.get("is_worsening"):
            worsening += 1
        elif prog == "improving":
            improving += 1
            
    # Check historical severity for same symptoms if history is provided
    if history:
        hist_sev_map = {}
        for h in history:
            code = h.get("symptom_code") or h.get("code")
            if code and code not in hist_sev_map:
                hist_sev_map[code] = h.get("severity", 0)
                
        for s in current_symptoms:
            code = s.get("code") or s.get("symptom_code")
            if code in hist_sev_map:
                curr_sev = s.get("severity", 0)
                prev_sev = hist_sev_map[code]
                if curr_sev > prev_sev:
                    worsening += 1
                elif curr_sev < prev_sev:
                    improving += 1

    trend_score = float(worsening - improving)
    
    if trend_score > 0.5:
        label = "worsening"
    elif trend_score < -0.5:
        label = "improving"
    elif current_symptoms:
        label = "stable"
    else:
        label = "unknown"
        
    return (trend_score, label)
