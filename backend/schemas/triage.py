"""
Pydantic Schemas for Triage Assessment API.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SymptomItem(BaseModel):
    code: str
    name: str
    severity: int = Field(default=5, ge=0, le=10)
    duration_value: Optional[int] = 1
    duration_unit: Optional[str] = "days"
    progression: Optional[str] = "unchanged"
    notes: Optional[str] = ""

class QuestionOptionSchema(BaseModel):
    code: str
    text: str
    triggers_emergency: bool = False

class FollowupQuestionSchema(BaseModel):
    question_id: str
    symptom_code: str
    question_text: str
    options: List[QuestionOptionSchema]
    is_required: bool = False
    priority: int = 1
    category: Optional[str] = None
    branching_logic: Optional[Dict[str, str]] = None

class AssessmentStartRequest(BaseModel):
    patient_id: Optional[int] = 1
    symptoms: List[SymptomItem]

class AssessmentStartResponse(BaseModel):
    session_id: str
    total_symptoms: int
    total_questions_budget: int
    first_question: Optional[FollowupQuestionSchema] = None

class NextQuestionRequest(BaseModel):
    session_id: str
    symptoms: List[SymptomItem]
    answers_so_far: Dict[str, str] = Field(default_factory=dict)
    current_question_id: Optional[str] = None
    current_answer: Optional[str] = None

class NextQuestionResponse(BaseModel):
    question: Optional[FollowupQuestionSchema] = None
    question_number: int
    total_estimated: int
    is_complete: bool

class AssessmentEvaluateRequest(BaseModel):
    session_id: Optional[str] = None
    patient_id: Optional[int] = 1
    symptoms: List[SymptomItem]
    followup_answers: Dict[str, str] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)

class TriageResultResponse(BaseModel):
    session_id: str
    urgency_category: int
    urgency_label: str
    started_at: str
    completed_at: str
    severity_score: float
    progression_trend: str
    emergency_override: bool
    warning_signs_found: List[str]
    rules_triggered: List[Dict[str, Any]]
    contradictions: List[str]
    missing_critical_data: List[str]
    summary_explanation: str
    detailed_reasoning: List[str]
    recommended_next_steps: List[str]
    uncertainty_statement: str
    clinical_limitations: str
    triage_version: str = "1.0.0"
