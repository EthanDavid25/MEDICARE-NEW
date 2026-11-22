"""
API Router for Clinical Symptom Assessment and Adaptive Questionnaire.
Directly wraps the authoritative Python TriageEngine and AdaptiveQuestionEngine.
"""
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.triage import (
    SymptomItem, FollowupQuestionSchema,
    AssessmentStartRequest, AssessmentStartResponse,
    NextQuestionRequest, NextQuestionResponse,
    AssessmentEvaluateRequest, TriageResultResponse
)

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

def get_controller():
    from backend.main import get_app_controller
    return get_app_controller()

@router.get("/symptoms")
def get_all_symptoms(controller=Depends(get_controller)) -> List[Dict[str, Any]]:
    """Returns all 81 medical symptoms with codes, names, categories, and severities."""
    return controller.dataset_loader.get_symptoms()

@router.post("/start", response_model=AssessmentStartResponse)
def start_assessment(payload: AssessmentStartRequest, controller=Depends(get_controller)):
    """Initializes an adaptive questionnaire session for the given chief symptoms."""
    if not payload.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom must be selected.")

    symptom_dicts = [s.model_dump() for s in payload.symptoms]
    max_sev = max((s.severity for s in payload.symptoms), default=5)
    prog = payload.symptoms[0].progression if payload.symptoms else "unchanged"

    question_engine = controller.dataset_loader.get_question_engine()
    session = question_engine.create_session(
        symptoms=symptom_dicts,
        severity=max_sev,
        progression=prog or "unchanged"
    )

    session_id = f"SES_{uuid.uuid4().hex[:12].upper()}"
    first_q = session.get_next_question()
    first_q_schema = None
    if first_q:
        first_q_schema = FollowupQuestionSchema(
            question_id=first_q.get("question_id"),
            symptom_code=first_q.get("symptom_code", ""),
            question_text=first_q.get("question_text", ""),
            options=first_q.get("options", []),
            is_required=first_q.get("is_required", False),
            priority=first_q.get("priority", 1),
            category=first_q.get("category"),
            branching_logic=first_q.get("branching_logic")
        )

    return AssessmentStartResponse(
        session_id=session_id,
        total_symptoms=len(payload.symptoms),
        total_questions_budget=session.max_questions,
        first_question=first_q_schema
    )

@router.post("/next-question", response_model=NextQuestionResponse)
def get_next_question(payload: NextQuestionRequest, controller=Depends(get_controller)):
    """Computes the next adaptive question based on previous answers and branching logic."""
    symptom_dicts = [s.model_dump() for s in payload.symptoms]
    max_sev = max((s.severity for s in payload.symptoms), default=5)
    prog = payload.symptoms[0].progression if payload.symptoms else "unchanged"

    question_engine = controller.dataset_loader.get_question_engine()
    session = question_engine.create_session(
        symptoms=symptom_dicts,
        severity=max_sev,
        progression=prog or "unchanged"
    )

    # Replay answers so far to rebuild session state deterministically
    answers = dict(payload.answers_so_far)
    if payload.current_question_id and payload.current_answer:
        answers[payload.current_question_id] = payload.current_answer

    for qid, ans in answers.items():
        session.record_answer(qid, ans)

    next_q = session.get_next_question()
    next_q_schema = None
    if next_q:
        next_q_schema = FollowupQuestionSchema(
            question_id=next_q.get("question_id"),
            symptom_code=next_q.get("symptom_code", ""),
            question_text=next_q.get("question_text", ""),
            options=next_q.get("options", []),
            is_required=next_q.get("is_required", False),
            priority=next_q.get("priority", 1),
            category=next_q.get("category"),
            branching_logic=next_q.get("branching_logic")
        )

    answered_count = len(session.answers)
    return NextQuestionResponse(
        question=next_q_schema,
        question_number=answered_count + (1 if next_q else 0),
        total_estimated=max(session.max_questions, answered_count),
        is_complete=(next_q is None)
    )

@router.post("/evaluate", response_model=TriageResultResponse)
def evaluate_assessment(payload: AssessmentEvaluateRequest, controller=Depends(get_controller)):
    """
    Authoritative triage evaluation using the MEDICARE clinical engine.
    Applies the 22 clinical rules, 40 warning signs, severity metrics, and emergency escalation.
    """
    symptom_dicts = [s.model_dump() for s in payload.symptoms]
    
    result = controller.triage_engine.assess(
        patient_id=payload.patient_id or 1,
        symptoms=symptom_dicts,
        followup_answers=payload.followup_answers,
        risk_factors=payload.risk_factors
    )

    # Store in controller for active session tracking
    controller.last_triage_result = result

    # Format rules without raw identifiers for clean client consumption
    formatted_rules = []
    for r in result.rules_triggered:
        if isinstance(r, dict):
            formatted_rules.append({
                "rule_id": r.get("rule_id", "RULE"),
                "description": r.get("description", ""),
                "explanation": r.get("explanation", r.get("description", "")),
                "urgency_category": r.get("urgency_category", 3)
            })
        else:
            formatted_rules.append({
                "rule_id": str(r),
                "description": str(r),
                "explanation": str(r),
                "urgency_category": 3
            })

    return TriageResultResponse(
        session_id=result.session_id,
        urgency_category=result.urgency_category,
        urgency_label=result.urgency_label,
        started_at=result.started_at,
        completed_at=result.completed_at,
        severity_score=result.severity_score,
        progression_trend=result.progression_trend,
        emergency_override=result.emergency_override,
        warning_signs_found=result.warning_signs_found,
        rules_triggered=formatted_rules,
        contradictions=result.contradictions,
        missing_critical_data=result.missing_critical_data,
        summary_explanation=result.summary_explanation,
        detailed_reasoning=result.detailed_reasoning,
        recommended_next_steps=result.recommended_next_steps,
        uncertainty_statement=result.uncertainty_statement,
        clinical_limitations=result.clinical_limitations,
        triage_version=result.triage_version
    )
