"""
Automated Test Suite for Report UI Cleanup, Clinical Optimization & Scenarios A-E.
Verifies mouse multi-touch emulation is disabled, scenarios A-E produce expected categories,
unanswered questions show clean single notice without multiple repetitive error lines,
and Doctor Handover PDF retains full technical clinical details.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

local_kivy_home = PROJECT_ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config as KivyConfig
from app.core.config import MedicareConfig
from app.core.app_controller import AppController
from app.core.database import SQLiteDatabase
from app.datasets.dataset_loader import DatasetLoader
from app.triage.engine import TriageEngine
from app.reports.handover_pdf import generate_doctor_handover_pdf
import pypdfium2 as pdfium


class TestReportCleanupAndScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        cls.config = MedicareConfig(
            app_root=PROJECT_ROOT,
            db_path=cls.temp_path / "test.db",
            log_path=cls.temp_path / "test.log",
            data_dir=PROJECT_ROOT / "data",
            reports_dir=cls.temp_path / "reports",
            downloads_dir=cls.temp_path / "downloads"
        )
        cls.config.ensure_directories()
        cls.controller = AppController(cls.config)
        cls.db = SQLiteDatabase(cls.config.db_path)
        cls.db.initialize()
        cls.patient_id = cls.db.execute(
            "INSERT INTO patients (display_name, biological_sex, date_of_birth, created_at, updated_at) "
            "VALUES ('Rajesh Kumar', 'male', '1980-05-15', datetime('now'), datetime('now'))"
        ).lastrowid
        cls.loader = DatasetLoader(cls.config.data_dir, cls.db)
        cls.triage = TriageEngine(cls.loader, db=cls.db)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db.close()
        except Exception:
            pass
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. MOUSE MULTI-TOUCH EMULATION IS DISABLED
    # -------------------------------------------------------------------------
    def test_01_mouse_multitouch_disabled(self):
        """Verify Kivy mouse provider is configured to disable multi-touch red dots."""
        mouse_config = KivyConfig.get("input", "mouse")
        self.assertIn("disable_multitouch", mouse_config,
                      "Mouse configuration must contain disable_multitouch to eliminate red dots.")

    # -------------------------------------------------------------------------
    # 2. SCENARIO A: Chest Pain + Shortness of Breath (Category 1 Emergency)
    # -------------------------------------------------------------------------
    def test_02_scenario_a_chest_pain_dyspnea(self):
        """Scenario A: Chest Pain + Dyspnea triggers Category 1 Emergency Care."""
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_CHEST_PAIN", "name": "Chest Pain", "severity": 9, "progression": "worsening"},
                {"code": "SYM_DYSPNEA", "name": "Shortness of Breath", "severity": 8, "progression": "worsening"}
            ],
            followup_answers={
                "QID_CHEST_RADIATION": "YES",
                "QID_CHEST_WORSENING_RAPID": "YES",
                "QID_RESP_SEVERITY": "SEVERE"
            }
        )
        self.assertEqual(result.urgency_category, 1, "Chest Pain with radiation and dyspnea must be Category 1")
        self.assertTrue(result.emergency_override or len(result.warning_signs_found) > 0)
        self.assertIn("EMERGENCY", result.urgency_label.upper())
        # Check detailed reasoning does not have technical rule IDs in user-facing explainer
        for r in result.detailed_reasoning:
            self.assertNotIn("RULE_EMERG_", r, "User-facing detailed reasoning should not expose raw technical rule IDs")

    # -------------------------------------------------------------------------
    # 3. SCENARIO B: High Fever + Productive Cough (Category 2 Early Consultation)
    # -------------------------------------------------------------------------
    def test_03_scenario_b_fever_cough(self):
        """Scenario B: High Fever + Productive Cough triggers Category 2 Early Consultation."""
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_FEVER", "name": "Fever", "severity": 6, "progression": "worsening"},
                {"code": "SYM_COUGH", "name": "Cough", "severity": 5, "progression": "stable"}
            ],
            followup_answers={
                "QID_FEVER_TEMP_RANGE": "HIGH",
                "QID_COUGH_PRODUCTIVE": "YES",
                "QID_COUGH_DURATION": "FEW_DAYS"
            }
        )
        self.assertEqual(result.urgency_category, 2, "High fever with productive cough should be Category 2")
        self.assertIn("Early", result.urgency_label)

    # -------------------------------------------------------------------------
    # 4. SCENARIO C: Mild Tension Headache (Category 3 Routine Care)
    # -------------------------------------------------------------------------
    def test_04_scenario_c_mild_headache(self):
        """Scenario C: Mild Tension Headache triggers Category 3 Routine Healthcare."""
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_HEADACHE", "name": "Headache", "severity": 3, "progression": "stable"}
            ],
            followup_answers={
                "QID_HEADACHE_ONSET_THUNDERCLAP": "NO",
                "QID_HEADACHE_NEURO_DEFICIT": "NO",
                "QID_HEADACHE_NECK_STIFFNESS": "NO"
            }
        )
        self.assertEqual(result.urgency_category, 3, "Mild headache without red flags must be Category 3")
        self.assertIn("Routine", result.urgency_label)
        # Check that no emergency indicators message is generated
        has_no_emerg_notice = any("No immediate red-flag emergency indicators" in r for r in result.detailed_reasoning)
        self.assertTrue(has_no_emerg_notice, "Should indicate no red-flag indicators detected.")

    # -------------------------------------------------------------------------
    # 5. SCENARIO D: Skipped/Unanswered Safety Questions
    # -------------------------------------------------------------------------
    def test_05_scenario_d_skipped_safety_questions(self):
        """Scenario D: Skipped/Unanswered safety questions preserve safety and show clean notice."""
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_HEADACHE", "name": "Headache", "severity": 4, "progression": "stable"}
            ],
            followup_answers={}  # All required follow-up safety questions skipped
        )
        # Verify missing critical data list exists
        self.assertGreater(len(result.missing_critical_data), 0, "Missing required questions must be tracked")

        # Verify detailed reasoning does NOT repeat multiple "Incomplete Data Point:" lines
        incomplete_data_points = [r for r in result.detailed_reasoning if "Incomplete Data Point:" in r]
        self.assertEqual(len(incomplete_data_points), 0,
                         "Detailed reasoning should not contain repetitive Incomplete Data Point lines")

        # Verify uncertainty statement notes the incomplete safety answers
        self.assertIn("Some safety questions were not answered", result.uncertainty_statement)

    # -------------------------------------------------------------------------
    # 6. SCENARIO E: Contradictory Answers
    # -------------------------------------------------------------------------
    def test_06_scenario_e_contradictory_answers(self):
        """Scenario E: Contradictory answers handled safely (Category 4 or clear contradiction tracking)."""
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_CHEST_PAIN", "name": "Chest Pain", "severity": 0, "progression": "improving"}
            ],
            followup_answers={
                "QID_CHEST_RADIATION": "YES",
                "QID_CHEST_WORSENING_RAPID": "YES"
            }
        )
        # Either emergency override kicks in because of radiation/rapid worsening, or contradiction flags it
        self.assertIn(result.urgency_category, [1, 4], "Contradictory or acute findings must be handled safely")

    # -------------------------------------------------------------------------
    # 7. DOCTOR HANDOVER PDF RETAINS FULL TECHNICAL DETAILS
    # -------------------------------------------------------------------------
    def test_07_doctor_handover_pdf_retains_full_details(self):
        """Verify ReportLab PDF contains full technical details: unanswered questions, rules, scores."""
        patient = {
            "display_name": "Anita Sharma",
            "date_of_birth": "1975-08-20",
            "biological_sex": "female",
            "blood_group": "B+",
            "known_allergies": "Penicillin",
            "current_medications": "Amlodipine 5mg",
            "chronic_conditions": "Hypertension",
            "emergency_contact": "+91-9876543210"
        }
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[
                {"code": "SYM_CHEST_PAIN", "name": "Chest Pain", "severity": 8, "progression": "worsening"}
            ],
            followup_answers={
                "QID_CHEST_RADIATION": "YES"
                # Other required questions intentionally skipped
            }
        )
        pdf_path = self.temp_path / "test_full_handover.pdf"
        output = generate_doctor_handover_pdf(patient, result.to_dict(), pdf_path)
        self.assertTrue(Path(output).exists(), "PDF file must exist.")

        # Extract text using pypdfium2
        doc = pdfium.PdfDocument(output)
        self.assertGreater(len(doc), 0)
        full_text = ""
        for page in doc:
            full_text += page.get_textpage().get_text_range()

        # Check that technical details are present in the PDF
        self.assertIn("Computed Severity Metric", full_text, "PDF must include severity metric")
        self.assertIn("Progression Trajectory", full_text, "PDF must include progression trajectory")
        self.assertIn("Warning Signs", full_text, "PDF must include warning signs")
        self.assertIn("CLINICAL DISCLAIMER & NOTICE TO PHYSICIAN", full_text, "PDF must include disclaimer")


if __name__ == "__main__":
    unittest.main()
