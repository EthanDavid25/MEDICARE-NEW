"""
MEDICARE Triage Assessment Result Model.
Represents an explainable, structured triage evaluation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class TriageResult:
    session_id: str
    urgency_category: int          # 1: Emergency, 2: Early Consultation, 3: Routine, 4: Insufficient Info
    urgency_label: str             # Human-readable title
    started_at: str
    completed_at: str
    
    # Inputs
    symptoms: list[dict] = field(default_factory=list)
    followup_answers: dict[str, str] = field(default_factory=dict)
    risk_factors: list[str] = field(default_factory=list)
    
    # Evaluation details
    emergency_override: bool = False
    warning_signs_found: list[str] = field(default_factory=list)
    rules_triggered: list[dict] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    missing_critical_data: list[str] = field(default_factory=list)
    
    # Scoring & Progression
    severity_score: float = 0.0
    progression_trend: str = "unknown"  # "worsening", "improving", "stable", "unknown"
    
    # Explanations & Medical Navigation
    summary_explanation: str = ""
    detailed_reasoning: list[str] = field(default_factory=list)
    recommended_next_steps: list[str] = field(default_factory=list)
    uncertainty_statement: str = ""
    clinical_limitations: str = ""
    relevant_references: list[str] = field(default_factory=list)
    triage_version: str = "1.0.0"
    clinical_review_status: str = "NOT_REVIEWED - Educational and Demonstration Only"

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "urgency_category": self.urgency_category,
            "urgency_label": self.urgency_label,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "symptoms": self.symptoms,
            "followup_answers": self.followup_answers,
            "risk_factors": self.risk_factors,
            "emergency_override": self.emergency_override,
            "warning_signs_found": self.warning_signs_found,
            "rules_triggered": [r.get("rule_id", "") if isinstance(r, dict) else str(r) for r in self.rules_triggered],
            "contradictions": self.contradictions,
            "missing_critical_data": self.missing_critical_data,
            "severity_score": self.severity_score,
            "progression_trend": self.progression_trend,
            "summary_explanation": self.summary_explanation,
            "detailed_reasoning": self.detailed_reasoning,
            "recommended_next_steps": self.recommended_next_steps,
            "uncertainty_statement": self.uncertainty_statement,
            "clinical_limitations": self.clinical_limitations,
            "relevant_references": self.relevant_references,
            "triage_version": self.triage_version,
            "clinical_review_status": self.clinical_review_status
        }
