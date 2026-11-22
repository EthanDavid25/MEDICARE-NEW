"""
Unit tests for Doctor Handover Library Service, In-App PDF Rendering,
and India-Specific Mobile & Date Validation.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Redirect MEDICARE user-data to a temp dir so tests run in sandbox / CI
# without needing write access to %LOCALAPPDATA%.
_TEST_DATA_HOME = tempfile.mkdtemp(prefix="medicare_test_")
os.environ.setdefault("MEDICARE_DATA_HOME", _TEST_DATA_HOME)

local_kivy_home = PROJECT_ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from app.core.database import SQLiteDatabase
from app.history.handover_document_service import HandoverDocumentService
from app.security.india_validation import validate_indian_mobile, validate_indian_date, format_indian_datetime
from app.reports.handover_pdf import generate_doctor_handover_pdf


class TestIndiaValidation(unittest.TestCase):
    """Verifies strict Indian mobile and date validation rules."""

    def test_valid_indian_mobile_numbers(self):
        valid_inputs = [
            "+91 9876543210",
            "+91-98765-43210",
            "9876543210",
            "09876543210",
            "919876543210",
            "+918123456789",
            "+917012345678",
            "+916123456789",
        ]
        for num in valid_inputs:
            valid, norm, msg = validate_indian_mobile(num)
            self.assertTrue(valid, f"Expected {num} to be valid, but got: {msg}")
            self.assertTrue(norm.startswith("+91-"), f"Expected {norm} to start with +91-")
            self.assertEqual(len(norm.replace("+91-", "").replace("-", "")), 10)

    def test_foreign_numbers_rejected(self):
        foreign_inputs = [
            "+1 555 123 4567",
            "+44 20 7946 0958",
            "+61 412 345 678",
            "+81 90 1234 5678"
        ]
        for num in foreign_inputs:
            valid, norm, msg = validate_indian_mobile(num)
            self.assertFalse(valid, f"Expected {num} to be rejected")
            self.assertIn("Indian mobile numbers only", msg)

    def test_invalid_starting_digits_rejected(self):
        # 10 digits but starting with 1, 2, 3, 4, 5
        invalid_starters = [
            "1234567890",
            "2345678901",
            "3456789012",
            "4567890123",
            "5678901234",
            "+91-55555-55555"
        ]
        for num in invalid_starters:
            valid, norm, msg = validate_indian_mobile(num)
            self.assertFalse(valid, f"Expected {num} to be rejected")
            self.assertIn("6, 7, 8, or 9", msg)

    def test_invalid_lengths_rejected(self):
        invalid_lengths = ["98765", "98765432100", "123", "+91 9876"]
        for num in invalid_lengths:
            valid, norm, msg = validate_indian_mobile(num)
            self.assertFalse(valid)
            self.assertIn("10-digit", msg)

    def test_indian_date_validation(self):
        valid, norm, msg = validate_indian_date("15/06/1990")
        self.assertTrue(valid)
        self.assertEqual(norm, "15/06/1990")

        # ISO to DD/MM/YYYY normalization
        valid, norm, msg = validate_indian_date("1995-12-25")
        self.assertTrue(valid)
        self.assertEqual(norm, "25/12/1995")

        # Invalid dates
        valid, norm, msg = validate_indian_date("invalid-date")
        self.assertFalse(valid)

        # Future date
        valid, norm, msg = validate_indian_date("01/01/2099")
        self.assertFalse(valid)
        self.assertIn("future", msg)


class TestHandoverDocumentService(unittest.TestCase):
    """Tests the HandoverDocumentService and SQLite metadata tracking."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_medicare.db"
        self.db = SQLiteDatabase(self.db_path)
        self.db.initialize()
        self.service = HandoverDocumentService(self.db)

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_register_and_retrieve_download(self):
        # Create a test dummy PDF file
        pdf_path = Path(self.temp_dir.name) / "test_report.pdf"
        pdf_path.write_text("%PDF-1.4 test dummy pdf content")

        doc = self.service.register_download(
            session_id="SES_TEST_001",
            patient_id=1,
            patient_name="Ethan Demonstration",
            title="Doctor Handover — SES_TEST_001",
            main_symptoms="Headache, Dizziness",
            pain_severity=6,
            triage_category=2,
            triage_label="Early Medical Consultation",
            file_path=pdf_path
        )

        self.assertIsNotNone(doc)
        self.assertTrue(doc["id"].startswith("DOC_"))
        self.assertEqual(doc["session_id"], "SES_TEST_001")
        self.assertEqual(doc["status"], "available")
        self.assertGreater(doc["file_size"], 0)

        # Retrieve all
        all_docs = self.service.get_downloaded_handovers()
        self.assertEqual(len(all_docs), 1)
        self.assertEqual(all_docs[0]["patient_name"], "Ethan Demonstration")

        # Search query matching
        matched = self.service.get_downloaded_handovers(search_query="Headache")
        self.assertEqual(len(matched), 1)

        unmatched = self.service.get_downloaded_handovers(search_query="NonExistent")
        self.assertEqual(len(unmatched), 0)

    def test_export_and_delete_download(self):
        pdf_path = Path(self.temp_dir.name) / "test_export_doc.pdf"
        pdf_path.write_text("%PDF-1.4 test content for export")

        doc = self.service.register_download(
            session_id="SES_TEST_002",
            patient_id=1,
            patient_name="Ethan",
            title="Doctor Handover — SES_TEST_002",
            main_symptoms="Fever",
            pain_severity=4,
            triage_category=3,
            triage_label="Routine Healthcare",
            file_path=pdf_path
        )

        export_dir = Path(self.temp_dir.name) / "exports"
        exported = self.service.export_copy(doc["id"], export_dir)
        self.assertIsNotNone(exported)
        self.assertTrue(Path(exported).exists())

        # Test deletion
        deleted = self.service.delete_handover(doc["id"], delete_file=True)
        self.assertTrue(deleted)
        self.assertFalse(pdf_path.exists())
        self.assertIsNone(self.service.get_handover_by_id(doc["id"]))


class TestInAppPDFRendering(unittest.TestCase):
    """Verifies pypdfium2 renders clinical handover PDFs correctly."""

    def test_render_handover_pdf_pages(self):
        import pypdfium2 as pdfium
        # Check existing audit report
        pdf_path = PROJECT_ROOT / "data" / "reports" / "Audit_Handover_SES_0C9E69B5E735.pdf"
        if pdf_path.exists():
            doc = pdfium.PdfDocument(str(pdf_path))
            self.assertGreater(len(doc), 0)
            page = doc[0]
            bitmap = page.render(scale=1.5)
            pil_img = bitmap.to_pil()
            self.assertGreater(pil_img.width, 400)
            self.assertGreater(pil_img.height, 500)


if __name__ == "__main__":
    unittest.main()
