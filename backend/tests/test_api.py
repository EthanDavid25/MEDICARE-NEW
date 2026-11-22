"""
Comprehensive Unit & Integration Tests for MEDICARE Mobile Backend API.
Tests all endpoints: Health, Symptoms, Adaptive Questionnaire, Triage Evaluation,
Hospital Search, Indian Mobile Validation, PDF Generation, and Dataset Sync.
Runs directly against endpoint functions with zero network/socket dependencies.
"""
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Safe test environment
os.environ["MEDICARE_DATA_HOME"] = str(Path(os.environ.get("TEMP", "/tmp")) / "medicare_api_test")
os.environ["KIVY_HOME"] = str(PROJECT_ROOT / ".kivy_home")

from backend.main import get_app_controller
from backend.schemas.triage import (
    SymptomItem, AssessmentStartRequest, NextQuestionRequest, AssessmentEvaluateRequest
)
from backend.schemas.patient import PatientCreateRequest
from backend.api.assessment import get_all_symptoms, start_assessment, get_next_question, evaluate_assessment
from backend.api.hospitals import get_nearby_hospitals, get_facility_by_id
from backend.api.patients import register_or_update_patient, get_patient
from backend.api.reports import create_handover_pdf, HandoverGenerateRequest
from backend.api.sync import get_offline_sync_bundle
from fastapi import HTTPException

class TestMobileBackendAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = get_app_controller()

    # 1. Health Check & Datasets Verification
    def test_01_health_and_datasets(self):
        loader = self.controller.dataset_loader
        symptoms = loader.get_symptoms()
        rules = loader.get_triage_rules()
        questions = loader.get_followup_questions()
        facilities = loader.get_facilities()
        self.assertEqual(len(symptoms), 81, "Must load all 81 symptoms")
        self.assertEqual(len(rules), 22, "Must load all 22 triage rules")
        self.assertEqual(len(questions), 28, "Must load all 28 follow-up questions")
        self.assertEqual(len(facilities), 14, "Must load 14 Maharashtra facilities")

    # 2. Symptoms List Endpoint
    def test_02_get_all_symptoms(self):
        symptoms = get_all_symptoms(self.controller)
        self.assertEqual(len(symptoms), 81)
        s0 = symptoms[0]
        self.assertIn("code", s0)
        self.assertIn("name", s0)
        self.assertIn("body_system", s0)

    # 3. Start Adaptive Assessment Endpoint
    def test_03_start_adaptive_assessment(self):
        payload = AssessmentStartRequest(
            symptoms=[SymptomItem(code="SYM_CHEST_PAIN", name="Chest Pain", severity=8, progression="worsening")]
        )
        res = start_assessment(payload, self.controller)
        self.assertTrue(res.session_id.startswith("SES_"))
        self.assertGreater(res.total_questions_budget, 0)
        self.assertIsNotNone(res.first_question)
        self.assertIn("question_id", res.first_question.model_dump())
        # Verify strict <=7 words constraint
        word_count = len(res.first_question.question_text.split())
        self.assertLessEqual(word_count, 7, f"Question text must be <= 7 words: '{res.first_question.question_text}'")

    # 4. Next Question & Dynamic Branching Endpoint
    def test_04_next_question_adaptive(self):
        payload = NextQuestionRequest(
            session_id="SES_TEST_01",
            symptoms=[SymptomItem(code="SYM_CHEST_PAIN", name="Chest Pain", severity=8)],
            answers_so_far={"QID_CHEST_RADIATION": "YES"}
        )
        res = get_next_question(payload, self.controller)
        self.assertGreaterEqual(res.question_number, 1)
        self.assertIn(res.is_complete, [True, False])

    # 5. Authoritative Triage Evaluation - Emergency (Category 1)
    def test_05_evaluate_emergency_scenario(self):
        payload = AssessmentEvaluateRequest(
            session_id="SES_EMERG_01",
            symptoms=[
                SymptomItem(code="SYM_CHEST_PAIN", name="Chest Pain", severity=9, progression="worsening"),
                SymptomItem(code="SYM_DYSPNEA", name="Shortness of Breath", severity=8, progression="worsening")
            ],
            followup_answers={
                "QID_CHEST_RADIATION": "YES",
                "QID_CHEST_WORSENING_RAPID": "YES",
                "QID_RESP_SEVERITY": "SEVERE"
            }
        )
        res = evaluate_assessment(payload, self.controller)
        self.assertEqual(res.urgency_category, 1, "Acute chest pain + dyspnea must be Category 1 Emergency")
        self.assertIn("EMERGENCY", res.urgency_label.upper())
        self.assertTrue(res.emergency_override or len(res.warning_signs_found) > 0)
        self.assertGreater(len(res.recommended_next_steps), 0)

    # 6. Authoritative Triage Evaluation - Routine (Category 3)
    def test_06_evaluate_routine_scenario(self):
        payload = AssessmentEvaluateRequest(
            session_id="SES_ROUTINE_01",
            symptoms=[SymptomItem(code="SYM_HEADACHE", name="Headache", severity=3, progression="unchanged")],
            followup_answers={
                "QID_HEADACHE_ONSET_THUNDERCLAP": "NO",
                "QID_HEADACHE_NEURO_DEFICIT": "NO",
                "QID_HEADACHE_NECK_STIFFNESS": "NO"
            }
        )
        res = evaluate_assessment(payload, self.controller)
        self.assertEqual(res.urgency_category, 3, "Mild tension headache without red flags must be Category 3")
        self.assertIn("Routine", res.urgency_label)

    # 7. Indian Mobile Number Validation - Valid (+91 / 10-digit) vs Invalid
    def test_07_patient_registration_validation(self):
        # Valid Indian Mobile
        valid_payload = PatientCreateRequest(
            display_name="Aarav Sharma",
            phone_number="+91 98765 43210",
            biological_sex="male",
            blood_group="O+"
        )
        patient = register_or_update_patient(valid_payload, self.controller)
        self.assertIsNotNone(patient.id)
        self.assertIn("98765", patient.phone_number)
        self.assertTrue(patient.phone_number.startswith("+91"))

        # Invalid International Mobile (should raise HTTPException 422)
        invalid_payload = PatientCreateRequest(
            display_name="John Doe",
            phone_number="+1 415 555 2671"
        )
        with self.assertRaises(HTTPException) as ctx:
            register_or_update_patient(invalid_payload, self.controller)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("supports Indian mobile numbers only", ctx.exception.detail)

    # 8. Nearby Hospitals Search Endpoint (GPS and Locality)
    def test_08_hospitals_search(self):
        # GPS coordinates search near Mumbai
        res_gps = get_nearby_hospitals(latitude=18.99, longitude=72.84, radius_km=30.0, emergency_only=False, locality=None, controller=self.controller)
        self.assertGreater(res_gps.total, 0)
        first_hosp = res_gps.facilities[0]
        self.assertIsNotNone(first_hosp.distance_km)
        self.assertEqual(first_hosp.state, "Maharashtra")

        # Locality search by keyword
        res_loc = get_nearby_hospitals(locality="Mumbai", radius_km=50.0, emergency_only=False, latitude=None, longitude=None, controller=self.controller)
        self.assertGreater(res_loc.total, 0)

        # Get by facility ID
        fac_id = first_hosp.id
        single_fac = get_facility_by_id(fac_id, self.controller)
        self.assertEqual(single_fac.id, fac_id)

    # 9. Handover PDF Generation
    def test_09_generate_handover_pdf(self):
        payload = HandoverGenerateRequest(
            session_id="SES_MOBILE_PDF_01",
            patient_id=1,
            triage_result={
                "session_id": "SES_MOBILE_PDF_01",
                "urgency_category": 2,
                "urgency_label": "Category 2 — Early Medical Consultation",
                "completed_at": "2026-11-22T13:00:00",
                "severity_score": 6.5,
                "progression_trend": "worsening",
                "summary_explanation": "Early medical consultation advised within 24 hours.",
                "symptoms": [{"code": "SYM_FEVER", "name": "Fever", "severity": 6}],
                "warning_signs_found": [],
                "rules_triggered": ["RULE_FEVER_PERSISTENT"],
                "missing_critical_data": ["Unanswered question: Chills present?"],
                "recommended_next_steps": ["Schedule clinical appointment today or tomorrow."]
            }
        )
        res = create_handover_pdf(payload, self.controller)
        self.assertEqual(res.session_id, "SES_MOBILE_PDF_01")
        self.assertTrue(res.pdf_filename.endswith(".pdf"))
        self.assertGreater(res.file_size_bytes, 1000)

    # 10. Offline Dataset Synchronization Bundle
    def test_10_offline_dataset_sync(self):
        bundle = get_offline_sync_bundle(self.controller)
        self.assertEqual(bundle["version"], "1.0.0")
        self.assertEqual(len(bundle["symptoms"]), 81)
        self.assertEqual(len(bundle["triage_rules"]), 22)
        self.assertEqual(len(bundle["warning_signs"]), 40)
        self.assertEqual(len(bundle["followup_questions"]), 28)
        self.assertEqual(len(bundle["facilities"]), 14)

if __name__ == "__main__":
    unittest.main()
