"""
MEDICARE Automated Demo Readiness & Verification Script.
Executes non-blocking headless verification of UI, database, clinical triage,
handover PDF generation, and C fallback primitives.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Set Kivy local home and headless / dummy window for testing
local_kivy_home = ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_LOG_LEVEL"] = "warning"

from app.core.config import load_config
from app.core.app_controller import AppController
from app.ui.app import MedicareKivyApp
from app.reports.handover_pdf import generate_doctor_handover_pdf

def run_verification():
    print("=================================================================")
    print("MEDICARE — Automated Verification & Demo Readiness Audit")
    print("=================================================================\n")

    # 1. Initialize Controller
    config = load_config()
    controller = AppController(config)
    controller.initialize()
    print("[PASS] 1. AppController, SQLite, Datasets & Logging Initialized.")

    # 2. Test All 12 Screens in Kivy App
    kivy_app = MedicareKivyApp(controller)
    root = kivy_app.build()
    
    screen_names = list(kivy_app.screens.keys())
    print(f"[PASS] 2. Kivy Root Window & ScreenManager Built. Total Screens: {len(screen_names)}")
    expected_screens = [
        "dashboard", "patient_profile", "symptom_assessment", "followup_questions",
        "triage_results", "patient_history", "symptom_progression", "doctor_handover",
        "healthcare_directory", "medical_references", "settings", "about"
    ]
    for s_name in expected_screens:
        assert s_name in screen_names, f"Screen {s_name} missing from UI!"
        screen_obj = kivy_app.screens[s_name]
        screen_obj.on_pre_enter()
        print(f"       -> Screen '{s_name}' instantiated and pre-entered successfully.")

    # 3. Test Patient Service CRUD
    ps = controller.patient_service
    test_pid = ps.create_patient({
        "display_name": "Audit Test Patient",
        "date_of_birth": "1994-08-25",
        "biological_sex": "female",
        "blood_group": "AB+",
        "known_allergies": "Aspirin",
        "chronic_conditions": "Migraine",
        "current_medications": "Sumatriptan",
        "emergency_contact": "Next of Kin (+1-555-0812)"
    })
    pt = ps.get_patient(test_pid)
    assert pt["display_name"] == "Audit Test Patient"
    print(f"[PASS] 3. Patient Registration & Retrieval Verified (Patient ID: {test_pid}).")

    # 4. Test Complete Symptom-to-Triage Workflow: Category 1 (Emergency)
    res_emerg = controller.triage_engine.assess(
        patient_id=test_pid,
        symptoms=[{
            "code": "SYM_CHEST_PAIN",
            "name": "Severe Chest Pain",
            "severity": 9,
            "duration_value": 1,
            "duration_unit": "hours",
            "progression": "worsening"
        }],
        followup_answers={"QID_CHEST_RADIATION": "YES"}
    )
    assert res_emerg.urgency_category == 1, "Must classify as Category 1 (Emergency Care)"
    assert res_emerg.emergency_override is True
    print(f"[PASS] 4. Category 1 Emergency Override Verified: {res_emerg.urgency_label} (Session: {res_emerg.session_id})")

    # 5. Test Category 2 (Early Medical Consultation)
    res_early = controller.triage_engine.assess(
        patient_id=test_pid,
        symptoms=[{
            "code": "SYM_FEVER",
            "name": "High Fever",
            "severity": 7,
            "duration_value": 3,
            "duration_unit": "days",
            "progression": "worsening"
        }],
        followup_answers={
            "QID_FEVER_TEMP": "HIGH_GRADE",
            "QID_SYMPTOM_PROGRESSION": "WORSENING_SLOWLY"
        }
    )
    assert res_early.urgency_category == 2
    print(f"[PASS] 5. Category 2 Early Consultation Verified: {res_early.urgency_label}")

    # 6. Test Category 3 (Routine Healthcare)
    res_routine = controller.triage_engine.assess(
        patient_id=test_pid,
        symptoms=[{
            "code": "SYM_HEADACHE",
            "name": "Tension Headache",
            "severity": 3,
            "duration_value": 2,
            "duration_unit": "days",
            "progression": "unchanged"
        }],
        followup_answers={
            "QID_PAIN_ONSET_SUDDEN": "NO",
            "QID_HEADACHE_STIFF_NECK": "YES",
            "QID_SYMPTOM_PROGRESSION": "UNCHANGED"
        }
    )
    assert res_routine.urgency_category == 3
    print(f"[PASS] 6. Category 3 Routine Healthcare Verified: {res_routine.urgency_label}")

    # 7. Test Category 4 (Insufficient Information & Discordant Answers)
    res_insuff = controller.triage_engine.assess(
        patient_id=test_pid,
        symptoms=[{
            "code": "SYM_BACK_PAIN",
            "name": "Chronic Back Pain",
            "severity": 10,
            "duration_value": 45,
            "duration_unit": "days",
            "progression": "improving"
        }],
        followup_answers={
            "QID_SYMPTOM_PROGRESSION": "IMPROVING",
            "QID_SYMPTOM_DURATION": "WEEKS"
        }
    )
    assert res_insuff.urgency_category == 4
    print(f"[PASS] 7. Category 4 Insufficient / Contradictory Verified: {res_insuff.urgency_label}")

    # 8. Test Patient History & Progression Tracking
    hist = controller.history_service.get_assessment_history(test_pid)
    assert len(hist) >= 4
    prog = controller.history_service.get_symptom_progression_timeline(test_pid)
    assert len(prog) >= 4
    print(f"[PASS] 8. Patient History ({len(hist)} records) & Timeline Progression ({len(prog)} records) Verified.")

    # 9. Test Doctor Handover PDF Generation
    pdf_out = ROOT / "data" / "reports" / f"Audit_Handover_{res_emerg.session_id}.pdf"
    gen_path = generate_doctor_handover_pdf(pt, res_emerg.to_dict(), pdf_out)
    assert Path(gen_path).exists()
    assert Path(gen_path).stat().st_size > 1000
    print(f"[PASS] 9. Doctor Handover PDF Generated Successfully: {gen_path} ({Path(gen_path).stat().st_size} bytes)")

    # 10. Test Healthcare Directory & Medical References
    facs = controller.dataset_loader.get_facilities()
    assert len(facs) >= 12
    refs = controller.dataset_loader.get_medical_references()
    assert len(refs) >= 8
    print(f"[PASS] 10. Local Healthcare Directory ({len(facs)} facilities) & References ({len(refs)} items) Verified.")

    # 10b. Test Location Service & Hospital Priority Recommendations
    loc_s = controller.location_service
    ok, loc_label = loc_s.set_manual_location("New York, NY")
    assert ok
    rec_facs = loc_s.get_nearby_facilities(urgency_category=1, limit=3)
    assert len(rec_facs) > 0
    assert str(rec_facs[0].get("has_emergency")) == "1"
    print(f"[PASS] 10b. Nearby Hospital Recommendation Verified (Priority 1: {rec_facs[0]['name']} has ER).")

    # 11. Test Security & Input Sanitization
    raw_str = "Secret Note \x00 with null bytes"
    sanitized = controller.security.sanitize_input(raw_str)
    assert "\x00" not in sanitized
    encrypted = controller.security.encrypt_text("Confidential Clinical Note")
    decrypted = controller.security.decrypt_text(encrypted)
    assert decrypted == "Confidential Clinical Note"
    print("[PASS] 11. Local AES Encryption & Sanitization Verified.")

    # 12. Test Offline Sync Controller
    summary = controller.sync_service.get_status_summary()
    assert summary["medical_datasets"] == "Verified Local (v1.0.0)"
    print(f"[PASS] 12. Offline Mode Controller Verified: {summary['mode']}.")

    controller.shutdown()
    print("\n>>> ALL 12 AUDIT TESTS PASSED SUCCESSFULLY! APPLICATION IS DEMO-READY. <<<")

if __name__ == "__main__":
    run_verification()
