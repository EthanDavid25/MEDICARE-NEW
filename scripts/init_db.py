"""Standalone SQLite Database Seeding and Initialization Utility."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import load_config
from app.core.database import SQLiteDatabase
from app.datasets.dataset_loader import DatasetLoader
from app.patients.patient_service import PatientService

def main():
    print("Initializing MEDICARE SQLite Database...")
    cfg = load_config()
    cfg.ensure_directories()
    
    db = SQLiteDatabase(cfg.db_path)
    db.initialize()
    print(f"Schema created at: {cfg.db_path}")

    ds = DatasetLoader(cfg.data_dir, db)
    print(f"Loaded {len(ds.get_symptoms())} symptoms, {len(ds.get_triage_rules())} rules, {len(ds.get_facilities())} facilities.")

    ps = PatientService(db)
    pts = ps.get_all_patients()
    if not pts:
        pid = ps.create_patient({
            "display_name": "Demo Patient",
            "date_of_birth": "1992-04-10",
            "biological_sex": "female",
            "blood_group": "B+",
            "known_allergies": "None",
            "chronic_conditions": "None",
            "current_medications": "None",
            "emergency_contact": "Family Contact (+1-555-0100)"
        })
        print(f"Created initial demonstration profile (ID: {pid})")
    else:
        print(f"Existing profiles found: {len(pts)}")

    db.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    main()
