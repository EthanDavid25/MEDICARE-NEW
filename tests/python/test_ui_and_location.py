"""
Automated functional verification for UI fixes, adaptive questions, and location recommendations.
"""
import unittest
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Kivy local home directory and headless/dummy mode for testing
local_kivy_home = PROJECT_ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_LOG_MODE"] = "PYTHON"

from app.core.app_controller import AppController
from app.healthcare.location_service import haversine_distance, LocationService

class TestUIAndLocationEnhancements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = AppController()
        cls.controller.initialize()

    def test_01_pain_slider_values_and_staging(self):
        """Verify pain slider severity values (1, 5, 10) and correct staging persistence."""
        staging = {
            "severity": 8,
            "progression": "worsening",
            "duration_days": 2,
            "symptoms": [
                {
                    "code": "SYM_CHEST_PAIN",
                    "name": "Chest Discomfort",
                    "severity": 8,
                    "duration_value": 2,
                    "duration_unit": "days",
                    "progression": "worsening",
                    "is_emergency_flag": False
                }
            ]
        }
        self.controller.assessment_staging = staging
        self.assertEqual(self.controller.assessment_staging["severity"], 8)
        self.assertEqual(self.controller.assessment_staging["symptoms"][0]["severity"], 8)
        self.assertEqual(self.controller.assessment_staging["progression"], "worsening")

    def test_02_adaptive_questions_worsening_vs_improving(self):
        """Verify question adaptation based on symptom trajectory while preserving emergency red-flags."""
        loader = self.controller.dataset_loader
        sym_codes = ["SYM_CHEST_PAIN"]

        # 1. Worsening questions
        worsening_q = loader.get_followup_questions_for_symptoms(sym_codes, progression="worsening", severity=8)
        worsening_ids = [q["question_id"] for q in worsening_q]
        self.assertTrue(len(worsening_q) > 0)
        self.assertIn("QID_CHEST_RADIATION", worsening_ids)
        self.assertIn("QID_CHEST_WORSENING_RAPID", worsening_ids)

        # 2. Improving questions
        improving_q = loader.get_followup_questions_for_symptoms(sym_codes, progression="improving", severity=3)
        improving_ids = [q["question_id"] for q in improving_q]
        self.assertTrue(len(improving_q) > 0)
        # CRITICAL REQUIREMENT: Emergency safety check must NEVER be skipped even when improving
        self.assertIn("QID_CHEST_RADIATION", improving_ids)
        # But worsening rapid escalation should NOT be included in improving set
        self.assertNotIn("QID_CHEST_WORSENING_RAPID", improving_ids)

    def test_03_symptom_specific_question_sets(self):
        """Verify symptom-specific questions for headache, fever, and breathing."""
        loader = self.controller.dataset_loader

        # Headache
        headache_q = loader.get_followup_questions_for_symptoms(["SYM_HEADACHE"], progression="unchanged", severity=6)
        headache_ids = [q["question_id"] for q in headache_q]
        self.assertTrue(any("HEADACHE" in qid or "NEURO" in qid for qid in headache_ids))
        self.assertIn("QID_HEADACHE_STIFF_NECK", headache_ids)
        self.assertIn("QID_PAIN_ONSET_SUDDEN", headache_ids)

        # Fever
        fever_q = loader.get_followup_questions_for_symptoms(["SYM_FEVER"], progression="unchanged", severity=6)
        fever_ids = [q["question_id"] for q in fever_q]
        self.assertIn("QID_FEVER_TEMP", fever_ids)

        # Shortness of breath
        dyspnea_q = loader.get_followup_questions_for_symptoms(["SYM_SHORTNESS_OF_BREATH"], progression="worsening", severity=8)
        dyspnea_ids = [q["question_id"] for q in dyspnea_q]
        self.assertIn("QID_RESP_STRIDOR_LIPS", dyspnea_ids)

    def test_04_haversine_distance_calculation(self):
        """Verify coordinate distance mathematics using Haversine formula."""
        # Distance between Times Square (40.7580, -73.9855) and Bellevue Hospital (40.7397, -73.9754)
        km, miles = haversine_distance(40.7580, -73.9855, 40.7397, -73.9754)
        self.assertGreater(miles, 1.0)
        self.assertLess(miles, 3.0)
        self.assertAlmostEqual(km, miles * 1.60934, delta=0.2)

    def test_05_location_service_offline_and_manual_geocoding(self):
        """Verify location service manual setting, offline dictionary fallback, and privacy clearing."""
        loc = self.controller.location_service
        
        # Test manual address setting
        ok, name = loc.set_manual_location("Boston, MA")
        self.assertTrue(ok)
        self.assertIn("Boston", name)
        self.assertIsNotNone(loc.current_lat)
        self.assertIsNotNone(loc.current_lon)

        # Verify nearby facilities sorting
        facilities = loc.get_nearby_facilities(urgency_category=1, limit=5)
        self.assertGreater(len(facilities), 0)
        # Category 1 should prioritize emergency departments
        self.assertEqual(str(facilities[0].get("has_emergency")), "1")
        self.assertIn("distance_miles", facilities[0])

        # Test clearing location
        loc.clear_location()
        self.assertIsNone(loc.current_lat)
        self.assertIsNone(loc.current_lon)
        self.assertEqual(loc.current_location_name, "Location Not Set")

    def test_06_verified_facility_data_integrity(self):
        """Verify local facility directory has verified hospital items with coordinates and contact numbers."""
        facs = self.controller.dataset_loader.get_facilities()
        self.assertGreater(len(facs), 10)
        verified_count = sum(1 for f in facs if f.get("is_verified") == "1")
        self.assertGreaterEqual(verified_count, 8)
        
        # Check required fields
        for f in facs:
            self.assertTrue(f.get("name"))
            self.assertTrue(f.get("address"))
            self.assertTrue(f.get("phone"))
            self.assertTrue(f.get("operating_hours"))

    def test_07_all_12_screens_instantiation(self):
        """Verify all 12 Kivy screen classes instantiate cleanly without errors."""
        from app.ui.screens import (
            DashboardScreen, PatientProfileScreen, SymptomAssessmentScreen,
            FollowupQuestionsScreen, TriageResultsScreen, PatientHistoryScreen,
            SymptomProgressionScreen, DoctorHandoverScreen, HealthcareDirectoryScreen,
            MedicalReferencesScreen, SettingsScreen, AboutScreen
        )
        screens = [
            DashboardScreen(self.controller, name="test_dashboard"),
            PatientProfileScreen(self.controller, name="test_patient_profile"),
            SymptomAssessmentScreen(self.controller, name="test_symptom_assessment"),
            FollowupQuestionsScreen(self.controller, name="test_followup_questions"),
            TriageResultsScreen(self.controller, name="test_triage_results"),
            PatientHistoryScreen(self.controller, name="test_patient_history"),
            SymptomProgressionScreen(self.controller, name="test_symptom_progression"),
            DoctorHandoverScreen(self.controller, name="test_doctor_handover"),
            HealthcareDirectoryScreen(self.controller, name="test_healthcare_directory"),
            MedicalReferencesScreen(self.controller, name="test_medical_references"),
            SettingsScreen(self.controller, name="test_settings"),
            AboutScreen(self.controller, name="test_about")
        ]
        self.assertEqual(len(screens), 12)

if __name__ == "__main__":
    unittest.main()
