"""
MEDICARE Comprehensive Automated Test Suite.
Tests database operations, patient profiles, symptom validation,
rule engine evaluation, emergency overrides, all 4 triage categories,
contradiction checks, PDF generation, and offline guarantees.
"""
import sys
import unittest
import tempfile
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import MedicareConfig
from app.core.database import SQLiteDatabase
from app.core.native_loader import NativeLoader
from app.datasets.dataset_loader import DatasetLoader
from app.patients.patient_service import PatientService
from app.history.history_service import HistoryService
from app.triage.engine import TriageEngine
from app.reports.handover_pdf import generate_doctor_handover_pdf
from app.security.encryption import SecurityManager
from app.synchronization.sync_service import SyncService

class TestMedicareCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        
        cls.config = MedicareConfig(
            app_root=PROJECT_ROOT,
            db_path=cls.temp_path / "test_medicare.db",
            log_path=cls.temp_path / "test.log",
            data_dir=PROJECT_ROOT / "data",
            native_dir=PROJECT_ROOT / "native" / "build"
        )
        cls.config.ensure_directories()
        
        # Subsystems
        cls.db = SQLiteDatabase(cls.config.db_path)
        cls.db.initialize()
        cls.native = NativeLoader(cls.config.native_dir)
        cls.datasets = DatasetLoader(cls.config.data_dir, cls.db)
        cls.patients = PatientService(cls.db)
        cls.history = HistoryService(cls.db)
        cls.triage = TriageEngine(cls.datasets, cls.native, cls.db)
        cls.security = SecurityManager(cls.temp_path / ".key")
        cls.sync = SyncService(cls.config, cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temp_dir.cleanup()

    # ---------------------------------------------------------
    # 1. DATABASE & CONFIG
    # ---------------------------------------------------------
    def test_01_database_initialization(self):
        """Verify all required tables exist in SQLite database."""
        tables = [
            "patients", "assessments", "symptom_entries", "symptom_history",
            "followup_answers", "triage_rules", "facilities", "medical_references",
            "dataset_metadata", "app_settings", "audit_log"
        ]
        for tbl in tables:
            row = self.db.fetchone(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'")
            self.assertIsNotNone(row, f"Table {tbl} must exist in database schema.")

    # ---------------------------------------------------------
    # 2. PATIENT CRUD & VALIDATION
    # ---------------------------------------------------------
    def test_02_patient_registration_and_update(self):
        """Test patient creation, update, retrieval, and deletion."""
        pid = self.patients.create_patient({
            "display_name": "Test Subject Alpha",
            "date_of_birth": "1985-11-20",
            "biological_sex": "female",
            "blood_group": "A+",
            "known_allergies": "Amoxicillin",
            "chronic_conditions": "Mild Asthma",
            "current_medications": "Albuterol",
            "emergency_contact": "Bob (+1-555-0999)"
        })
        self.assertIsInstance(pid, int)
        
        # Fetch
        p = self.patients.get_patient(pid)
        self.assertEqual(p["display_name"], "Test Subject Alpha")
        self.assertEqual(p["blood_group"], "A+")

        # Update
        updated = self.patients.update_patient(pid, {"display_name": "Test Subject Beta", "biological_sex": "female"})
        self.assertTrue(updated)
        p_up = self.patients.get_patient(pid)
        self.assertEqual(p_up["display_name"], "Test Subject Beta")

        # Soft Delete
        del_ok = self.patients.delete_patient(pid, hard_delete=False)
        self.assertTrue(del_ok)
        self.assertIsNone(self.patients.get_patient(pid), "Soft-deleted patient should not be returned by get_patient")

    # ---------------------------------------------------------
    # 3. MEDICAL DATASET LOADING
    # ---------------------------------------------------------
    def test_03_medical_dataset_integrity(self):
        """Verify symptoms, warning signs, questions, rules, and facilities are loaded."""
        symptoms = self.datasets.get_symptoms()
        self.assertGreater(len(symptoms), 40, "At least 40 symptoms must be loaded.")
        
        warnings = self.datasets.get_warning_signs()
        self.assertGreater(len(warnings), 20, "At least 20 warning signs must be loaded.")

        rules = self.datasets.get_triage_rules()
        self.assertGreater(len(rules), 20, "At least 20 triage rules must be loaded.")

        facilities = self.datasets.get_facilities()
        self.assertGreater(len(facilities), 10, "At least 10 healthcare facilities must be loaded.")

    # ---------------------------------------------------------
    # 4. EMERGENCY OVERRIDE (CATEGORY 1)
    # ---------------------------------------------------------
    def test_04_emergency_override_chest_pain_radiation(self):
        """Verify Category 1 (Emergency Care) triggered by chest pain radiating to arm."""
        pid = self.patients.create_patient({"display_name": "Emergency Patient"})
        
        result = self.triage.assess(
            patient_id=pid,
            symptoms=[{
                "code": "SYM_CHEST_PAIN",
                "name": "Chest Pain",
                "severity": 8,
                "duration_value": 2,
                "duration_unit": "hours",
                "progression": "worsening"
            }],
            followup_answers={"QID_CHEST_RADIATION": "YES"}
        )
        self.assertEqual(result.urgency_category, 1, "Must assign Category 1 (Emergency Care).")
        self.assertIn("Emergency Care", result.urgency_label)
        self.assertTrue(result.emergency_override)
        self.assertGreater(len(result.warning_signs_found), 0)

    # ---------------------------------------------------------
    # 5. EARLY MEDICAL CONSULTATION (CATEGORY 2)
    # ---------------------------------------------------------
    def test_05_early_consultation_worsening_fever(self):
        """Verify Category 2 (Early Consultation) triggered by high fever or progressing symptoms."""
        pid = self.patients.create_patient({"display_name": "Fever Patient"})
        
        result = self.triage.assess(
            patient_id=pid,
            symptoms=[{
                "code": "SYM_FEVER",
                "name": "Fever",
                "severity": 6,
                "duration_value": 3,
                "duration_unit": "days",
                "progression": "worsening"
            }],
            followup_answers={
                "QID_FEVER_TEMP": "HIGH_GRADE",
                "QID_SYMPTOM_PROGRESSION": "WORSENING_SLOWLY"
            }
        )
        self.assertEqual(result.urgency_category, 2, "Must assign Category 2 (Early Medical Consultation).")
        self.assertIn("Early Medical Consultation", result.urgency_label)

    # ---------------------------------------------------------
    # 6. ROUTINE HEALTHCARE (CATEGORY 3)
    # ---------------------------------------------------------
    def test_06_routine_care_mild_symptom(self):
        """Verify Category 3 (Routine Healthcare) for mild, non-worsening symptoms."""
        pid = self.patients.create_patient({"display_name": "Routine Patient"})
        
        result = self.triage.assess(
            patient_id=pid,
            symptoms=[{
                "code": "SYM_HEADACHE",
                "name": "Mild Headache",
                "severity": 2,
                "duration_value": 1,
                "duration_unit": "days",
                "progression": "unchanged"
            }],
            followup_answers={
                "QID_PAIN_ONSET_SUDDEN": "NO",
                "QID_HEADACHE_STIFF_NECK": "YES",
                "QID_SYMPTOM_PROGRESSION": "UNCHANGED"
            }
        )
        self.assertEqual(result.urgency_category, 3, "Must assign Category 3 (Routine Healthcare).")

    # ---------------------------------------------------------
    # 7. CONTRADICTION & INSUFFICIENT INFO (CATEGORY 4)
    # ---------------------------------------------------------
    def test_07_insufficient_or_contradictory_handling(self):
        """Verify Category 4 (Insufficient Information) when answers are discordant or missing."""
        pid = self.patients.create_patient({"display_name": "Contradictory Patient"})
        
        result = self.triage.assess(
            patient_id=pid,
            symptoms=[{
                "code": "SYM_BACK_PAIN",
                "name": "Back Pain",
                "severity": 10,  # Extreme
                "duration_value": 30,
                "duration_unit": "days",
                "progression": "improving"
            }],
            followup_answers={
                "QID_SYMPTOM_PROGRESSION": "IMPROVING",
                "QID_SYMPTOM_DURATION": "WEEKS"
            }
        )
        # Severity 10 + duration weeks + improving triggers contradiction detector
        self.assertEqual(result.urgency_category, 4, "Must assign Category 4 (Insufficient Information).")
        self.assertGreater(len(result.contradictions), 0)

    # ---------------------------------------------------------
    # 8. DOCTOR HANDOVER PDF GENERATION
    # ---------------------------------------------------------
    def test_08_pdf_generation_offline(self):
        """Verify PDF handover summary generates without network access."""
        pid = self.patients.create_patient({
            "display_name": "PDF Test Patient",
            "known_allergies": "Latex",
            "chronic_conditions": "Hypertension"
        })
        patient = self.patients.get_patient(pid)
        
        result = self.triage.assess(
            patient_id=pid,
            symptoms=[{"code": "SYM_HEADACHE", "name": "Headache", "severity": 4}],
            followup_answers={}
        )
        
        pdf_path = self.temp_path / "test_handover.pdf"
        output = generate_doctor_handover_pdf(patient, result.to_dict(), pdf_path)
        
        self.assertTrue(Path(output).exists(), "Handover PDF must exist on disk.")
        self.assertGreater(Path(output).stat().st_size, 1000, "PDF must have non-trivial file size.")

    # ---------------------------------------------------------
    # 9. LOCAL SECURITY ENCRYPTION
    # ---------------------------------------------------------
    def test_09_local_encryption_and_sanitization(self):
        """Verify field encryption and input sanitization."""
        raw = "Sensitive Clinical Note: Patient exhibits mild tremor."
        enc = self.security.encrypt_text(raw)
        self.assertNotEqual(raw, enc)
        
        dec = self.security.decrypt_text(enc)
        self.assertEqual(raw, dec)

        # Sanitization
        dirty = "User\x00Name\x08With\nControl"
        clean = self.security.sanitize_input(dirty)
        self.assertNotIn("\x00", clean)
        self.assertNotIn("\x08", clean)

    # ---------------------------------------------------------
    # 10. OFFLINE GUARANTEE & SUMMARY
    # ---------------------------------------------------------
    def test_10_offline_operation_mode(self):
        """Verify all capabilities function with sync service reporting offline."""
        status = self.sync.get_status_summary()
        self.assertIn("local_database", status)
        self.assertIn("medical_datasets", status)
        
        verify = self.sync.verify_local_datasets()
        self.assertEqual(verify["status"], "VALID_LOCAL_STORE")

if __name__ == "__main__":
    unittest.main()
