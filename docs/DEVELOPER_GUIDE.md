# MEDICARE — Developer & Architecture Guide

---

## 1. System Architecture & Distribution
The MEDICARE project targets a clean architectural distribution:
- **Python (approx. 70%):** Core application orchestration, Kivy cross-platform UI, SQLite database operations, triage decision flow, report generation, and security services.
- **C (approx. 30%):** Native computational components in `native/src/`:
  - `symptom_processor.c`: Text normalization, lowercase conversion, and deduplication.
  - `rule_evaluator.c`: Bitfield-style rule matching and emergency overrides.
  - `data_validator.c`: Bound checking and contradiction detection.
  - `risk_calculator.c`: Weighted severity computations and trend delta calculations.
  - `triage_primitives.c`: Core urgency resolution algorithms.

---

## 2. Dynamic C Module Loader & Python Fallbacks
To guarantee 100% offline resilience and cross-platform flexibility across Android and Windows:
- `app/core/native_loader.py` dynamically checks for compiled shared libraries (`.dll` on Windows, `.so` on Android).
- If present, functions are called via `ctypes`.
- If absent, identical pure-Python fallback implementations in `app/core/fallback/` take over without any loss of functionality or crashes.

---

## 3. Directory Layout
```text
MEDICARE_OFFLINE/
├── app/
│   ├── core/                  # Engine orchestration, config, SQLite, native loader
│   │   └── fallback/          # Pure-Python mirrors of native C primitives
│   ├── datasets/              # Medical dataset parser & cache
│   ├── history/               # Assessment timeline & comparison service
│   ├── patients/              # Local profile management & CRUD
│   ├── reports/               # Offline ReportLab PDF handover generator
│   ├── security/              # Fernet symmetric encryption & input sanitizers
│   ├── synchronization/       # Network probe & offline status controller
│   ├── triage/                # Rule-based engine, explainer, result models
│   ├── ui/                    # Kivy cross-platform responsive GUI (12 screens)
│   └── main.py                # Main application launcher
├── data/
│   ├── database/              # SQLite database (medicare.db)
│   ├── healthcare/            # facilities.csv
│   └── medical/               # symptoms.json, warning_signs.json, triage_rules.json, etc.
├── docs/                      # User & Developer guides
├── native/
│   ├── include/               # medicare_types.h
│   ├── src/                   # C source files (5 modules)
│   └── build/                 # build.bat, CMakeLists.txt
├── scripts/                   # run_app.bat, init_db.py, build_windows_exe.bat
├── tests/                     # Automated unit and integration test suite
├── buildozer.spec             # Android APK build specification
├── medicare.spec              # PyInstaller Windows packaging specification
└── main.py                    # Root entry point
```

---

## 4. Running Tests
Execute the automated test suite using Python 3.11:
```bash
python -m unittest discover -s tests/python -p "test_*.py" -v
```
All 10 test modules evaluate:
- SQLite schema generation & foreign key compliance
- Patient CRUD operations
- Dataset integrity checks
- Category 1 Emergency Overrides
- Category 2 Early Medical Consultations
- Category 3 Routine Healthcare
- Category 4 Insufficient Information & Contradiction detection
- Local ReportLab PDF generation
- Symmetric Fernet encryption
- Autonomous offline operation
