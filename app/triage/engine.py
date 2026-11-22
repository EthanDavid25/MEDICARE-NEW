"""
MEDICARE Rule-Based Triage Engine.
Evaluates symptoms, duration, severity, follow-up answers, risk factors,
and historical trends to assign an explainable urgency category (1 to 4).
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Optional

from app.core.native_loader import NativeLoader
from app.datasets.dataset_loader import DatasetLoader
from app.triage.result import TriageResult
from app.triage.explainer import build_explanation, URGENCY_TITLES

logger = logging.getLogger("medicare.triage")

class TriageEngine:
    """Core rule-based assessment and clinical navigation engine."""

    def __init__(self, dataset_loader: DatasetLoader, native_loader: NativeLoader = None, db = None):
        self.datasets = dataset_loader
        self.native = native_loader or NativeLoader()
        self.db = db

    def assess(
        self,
        patient_id: int,
        symptoms: list[dict],
        followup_answers: dict[str, str],
        risk_factors: list[str] = None,
        patient_history: list[dict] = None
    ) -> TriageResult:
        """
        Executes complete rule-based triage assessment.
        """
        session_id = f"SES_{uuid.uuid4().hex[:12].upper()}"
        started_at = datetime.now().isoformat()
        risk_factors = risk_factors or []
        patient_history = patient_history or []
        
        logger.info("Initiating triage assessment for patient %s (Session %s)", patient_id, session_id)

        # Normalize followup answers and map rule aliases
        followup_answers = dict(followup_answers or {})
        if "QID_RESP_STRIDOR_LIPS" in followup_answers and "QID_RESP_STRIDOR" not in followup_answers:
            followup_answers["QID_RESP_STRIDOR"] = followup_answers["QID_RESP_STRIDOR_LIPS"]
        if "QID_FEVER_IMMUNO_RISK" in followup_answers and "QID_IMMUNOSUPPRESSED" not in followup_answers:
            followup_answers["QID_IMMUNOSUPPRESSED"] = followup_answers["QID_FEVER_IMMUNO_RISK"]
        if "QID_DIZZINESS_SYNCOPE" in followup_answers and "QID_SYNCOPE_EPISODE" not in followup_answers:
            followup_answers["QID_SYNCOPE_EPISODE"] = followup_answers["QID_DIZZINESS_SYNCOPE"]

        # 1. Clean & normalize symptoms
        processed_symptoms = []
        for s in symptoms:
            code = s.get("code") or s.get("symptom_code", "")
            raw_name = s.get("name") or s.get("symptom_name", "")
            norm_name = self.native.normalize_symptom(raw_name)
            
            # Lookup symptom definition in dataset to pull standard emergency flags
            ds_sym = self._find_dataset_symptom(code)
            is_emerg = s.get("is_emergency_flag", False) or (ds_sym.get("is_emergency_warning", False) if ds_sym else False)
            
            entry = {
                "code": code or (ds_sym.get("code") if ds_sym else "SYM_CUSTOM"),
                "name": raw_name or (ds_sym.get("name") if ds_sym else "Unspecified Symptom"),
                "severity": int(s.get("severity", 5)),
                "duration_value": int(s.get("duration_value", 1)),
                "duration_unit": s.get("duration_unit", "days"),
                "progression": s.get("progression", "unchanged"),
                "is_emergency_flag": is_emerg,
                "notes": s.get("notes", "")
            }
            processed_symptoms.append(entry)

        # Deduplicate symptoms (keeping higher severity)
        processed_symptoms = self.native.deduplicate_symptoms(processed_symptoms)

        # 2. Input validation & contradiction detection
        has_contradiction, contradictions = self.native.check_contradictions(processed_symptoms, followup_answers)

        # 3. Check for missing critical data
        missing_critical_data = []
        if not processed_symptoms:
            missing_critical_data.append("No primary symptoms selected.")

        # Check required questions
        required_questions = [
            q for q in self.datasets.get_followup_questions_for_symptoms([s["code"] for s in processed_symptoms])
            if q.get("is_required", False)
        ]
        for rq in required_questions:
            qid = rq["question_id"]
            if qid not in followup_answers or not followup_answers[qid]:
                missing_critical_data.append(f"Unanswered required safety question: {rq.get('question_text')}")

        # 4. Check Emergency Overrides (C primitive / fallback)
        has_emerg_override, warning_signs_found = self.native.check_emergency_override(
            processed_symptoms, self.datasets.get_warning_signs()
        )

        # Also check follow-up answers that trigger emergency checks
        for qid, ans in followup_answers.items():
            q_def = self._find_question(qid)
            if q_def:
                for opt in q_def.get("options", []):
                    if opt.get("code") == ans and opt.get("triggers_emergency", False):
                        has_emerg_override = True
                        warning_signs_found.append(f"Critical indicator confirmed: {q_def.get('question_text')} -> {opt.get('text')}")

        # 5. Evaluate all triage rules from dataset
        triggered_rules = []
        rule_categories = []
        all_rules = self.datasets.get_triage_rules()

        for rule in all_rules:
            if self.native.evaluate_rule(rule, processed_symptoms, followup_answers, risk_factors):
                triggered_rules.append(rule)
                rule_categories.append(rule.get("urgency_category", 3))

        # 6. Compute severity metric & trend
        severity_score = self.native.calculate_severity(processed_symptoms)
        trend_score, progression_trend = self.native.detect_progression(processed_symptoms, patient_history)

        # 7. Synthesize final Urgency Category
        # Hierarchy:
        # If contradiction or critical missing info AND no emergency override -> Category 4
        # If emergency override -> Category 1 (EMERGENCY ALWAYS OVERRIDES)
        # Else lowest integer category from rules (1 > 2 > 3)
        # If no rules triggered:
        #   If severity >= 8 -> Category 2
        #   If severity <= 3 -> Category 3
        #   Default -> Category 3
        if has_emerg_override:
            urgency_category = 1
        elif has_contradiction or (len(missing_critical_data) > 2 and len(processed_symptoms) == 0):
            urgency_category = 4
        elif rule_categories:
            urgency_category = self.native.find_highest_urgency(rule_categories)
        else:
            # Fallback algorithmic stratification
            if severity_score >= 8.0 or progression_trend == "worsening":
                urgency_category = 2
            else:
                urgency_category = 3

        urgency_label = URGENCY_TITLES.get(urgency_category, "Category 3 — Routine Healthcare")

        # 8. Generate transparent clinical explanations
        summary, detailed, next_steps, uncertainty, limitations = build_explanation(
            urgency_category=urgency_category,
            symptoms=processed_symptoms,
            followup_answers=followup_answers,
            rules_triggered=triggered_rules,
            warning_signs_found=warning_signs_found,
            contradictions=contradictions,
            missing_data=missing_critical_data,
            progression_trend=progression_trend,
            severity_score=severity_score
        )

        completed_at = datetime.now().isoformat()

        # Build Result Object
        result = TriageResult(
            session_id=session_id,
            urgency_category=urgency_category,
            urgency_label=urgency_label,
            started_at=started_at,
            completed_at=completed_at,
            symptoms=processed_symptoms,
            followup_answers=followup_answers,
            risk_factors=risk_factors,
            emergency_override=has_emerg_override,
            warning_signs_found=warning_signs_found,
            rules_triggered=triggered_rules,
            contradictions=contradictions,
            missing_critical_data=missing_critical_data,
            severity_score=severity_score,
            progression_trend=progression_trend,
            summary_explanation=summary,
            detailed_reasoning=detailed,
            recommended_next_steps=next_steps,
            uncertainty_statement=uncertainty,
            clinical_limitations=limitations,
            relevant_references=["REF_TRIAGE_PRINCIPLES", "REF_DISCLAIMER_LIMITATIONS"]
        )

        # 9. Persist to SQLite Database
        if self.db:
            self._save_to_database(patient_id, result)

        return result

    def _find_dataset_symptom(self, code: str) -> Optional[dict]:
        for s in self.datasets.get_symptoms():
            if s.get("code") == code:
                return s
        return None

    def _find_question(self, qid: str) -> Optional[dict]:
        for q in self.datasets._followup_questions:
            if q.get("question_id") == qid:
                return q
        return None

    def _save_to_database(self, patient_id: int, result: TriageResult):
        """Stores the completed assessment and individual symptom records."""
        try:
            # 1. Insert assessment record
            assessment_data = {
                "patient_id": patient_id,
                "session_id": result.session_id,
                "started_at": result.started_at,
                "completed_at": result.completed_at,
                "urgency_category": result.urgency_category,
                "urgency_label": result.urgency_label,
                "triage_version": result.triage_version,
                "rules_triggered": json.dumps([r.get("rule_id", "") for r in result.rules_triggered]),
                "explanation": result.summary_explanation,
                "raw_input": json.dumps({
                    "symptoms": result.symptoms,
                    "followup_answers": result.followup_answers,
                    "risk_factors": result.risk_factors
                }),
                "warnings_found": json.dumps(result.warning_signs_found),
                "is_deleted": 0
            }
            assessment_id = self.db.insert("assessments", assessment_data)

            # 2. Insert symptom entries
            for s in result.symptoms:
                sym_entry = {
                    "assessment_id": assessment_id,
                    "patient_id": patient_id,
                    "symptom_code": s.get("code", "UNKNOWN"),
                    "symptom_name": s.get("name", "Unknown"),
                    "reported_at": result.completed_at,
                    "duration_value": s.get("duration_value", 1),
                    "duration_unit": s.get("duration_unit", "days"),
                    "severity": s.get("severity", 5),
                    "progression": s.get("progression", "unchanged"),
                    "notes": s.get("notes", "")
                }
                self.db.insert("symptom_entries", sym_entry)
                
                # Also record in continuous symptom_history table
                self.db.insert("symptom_history", {
                    "patient_id": patient_id,
                    "symptom_code": s.get("code", "UNKNOWN"),
                    "symptom_name": s.get("name", "Unknown"),
                    "recorded_at": result.completed_at,
                    "duration_value": s.get("duration_value", 1),
                    "duration_unit": s.get("duration_unit", "days"),
                    "severity": s.get("severity", 5),
                    "progression": s.get("progression", "unchanged"),
                    "notes": s.get("notes", "")
                })

            # 3. Insert followup answers
            for qid, ans in result.followup_answers.items():
                q_def = self._find_question(qid)
                q_text = q_def.get("question_text", qid) if q_def else qid
                self.db.insert("followup_answers", {
                    "assessment_id": assessment_id,
                    "question_id": qid,
                    "question_text": q_text,
                    "answer_code": ans,
                    "answer_text": ans
                })

            self.db.log_audit_event("ASSESSMENT_COMPLETED", f"Assessment {result.session_id} saved for patient {patient_id}")
            logger.info("Successfully recorded assessment %s in database", result.session_id)
        except Exception as e:
            logger.error("Failed to save assessment %s to database: %s", result.session_id, e)
