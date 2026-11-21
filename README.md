# MEDICARE — Medical Symptoms Triage Advisor

> ⚕️ An offline-first desktop application for structured medical symptom triage and healthcare navigation.

---

## ⚠️ Medical Disclaimer

> **THIS APPLICATION IS NOT FOR CLINICAL USE.**
>
> MEDICARE is a decision-support and educational tool only. It does **not** provide medical diagnoses, replace professional medical advice, or constitute a clinical system. Always consult a qualified healthcare professional for any medical concern. In an emergency, call your local emergency services immediately (e.g., **911** in the USA, **999** in the UK, **112** in the EU).
>
> Triage recommendations produced by this application are based on generalised rule-based logic and are intended solely to help users organise and communicate their symptoms — not to substitute clinical judgement.

---

## Overview

MEDICARE is a cross-platform desktop application built with Python (PySide6) and native C modules. It enables users to:

- Log and track symptoms over time
- Receive structured triage guidance (urgency category 1–4)
- Find nearby healthcare facilities offline
- Maintain a local, encrypted patient profile
- Generate printable health summary reports

All data is stored **locally on-device** — no internet connection is required or used.

---

## Features

| Feature | Description |
|---|---|
| 🩺 Symptom Logger | Capture symptoms with severity, duration, and progression |
| 🚦 Triage Engine | Rule-based urgency categorisation (Emergency → Self-care) |
| 📋 Patient Profiles | Manage multiple patient records locally |
| 🏥 Facility Finder | Offline directory of hospitals, clinics, and pharmacies |
| 📈 History & Trends | Visual symptom trend charts (matplotlib) |
| 📄 PDF Reports | Generate printable assessment summaries (ReportLab) |
| 🔒 Security | Optional local encryption (cryptography library) |
| 🌐 Offline First | 100% air-gapped capable; no cloud dependency |

---

## Tech Stack

| Layer | Technology | Share |
|---|---|---|
| UI / Application | Python 3.15 · PySide6 · Qt6 | 70% |
| Triage Engine (native) | C99 · ctypes bridge | 30% |
| Data Visualisation | matplotlib 3.11 | — |
| PDF Generation | ReportLab 5.1 | — |
| Database | SQLite3 (stdlib) | — |
| Security | cryptography 50 | — |
| Packaging | PyInstaller 6.22 | — |

---

## Requirements

- **OS**: Windows 10/11 (primary), macOS 12+, Ubuntu 22.04+
- **Python**: 3.12+ (tested on 3.15.2)
- **Disk**: ~200 MB (application) + local data
- **RAM**: 512 MB minimum, 1 GB recommended
- **Display**: 1280×720 minimum

### Python dependencies

```
PySide6>=6.12.0
matplotlib>=3.11.0
reportlab>=5.1.0
cryptography>=50.0.0
pyinstaller>=6.22.0
numpy>=2.5.0
```

---

## Quick Start

### 1. Clone / extract the project

```bash
cd "C:\Users\ethan\OneDrive\Documents\Medicare new\MEDICARE_OFFLINE"
```

### 2. Install dependencies

```bash
"C:\Users\ethan\AppData\Local\Python\bin\pip.exe" install -r requirements.txt
```

### 3. Initialise the database

```bash
"C:\Users\ethan\AppData\Local\Python\bin\python.exe" scripts\init_db.py
```

### 4. Launch the application

```bash
"C:\Users\ethan\AppData\Local\Python\bin\python.exe" app\main.py
```

Or use the convenience launcher:

```bash
scripts\run_app.bat
```

---

## Project Structure

```
MEDICARE_OFFLINE/
├── app/
│   ├── main.py                  # Application entry point
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging setup
│   │   ├── database.py          # SQLite database layer
│   │   ├── native_loader.py     # C DLL loader with Python fallbacks
│   │   ├── app_controller.py    # Central application controller
│   │   └── fallback/            # Pure-Python fallback implementations
│   │       ├── symptom_processor.py
│   │       ├── rule_evaluator.py
│   │       ├── data_validator.py
│   │       └── risk_calculator.py
│   ├── ui/
│   │   ├── main_window.py       # Main application window
│   │   ├── pages/               # Full-screen page widgets
│   │   └── widgets/             # Reusable UI components
│   ├── triage/                  # Triage engine (Python side)
│   ├── patients/                # Patient management
│   ├── history/                 # Symptom history
│   ├── reports/                 # PDF report generation
│   ├── healthcare/              # Facility finder
│   ├── datasets/                # Dataset loader
│   └── security/                # Encryption utilities
├── native/
│   ├── include/                 # C header files
│   ├── src/                     # C source files
│   └── build/                   # Compiled DLLs
├── data/
│   ├── database/                # SQLite database file
│   ├── medical/                 # Medical JSON datasets
│   └── healthcare/              # Facility CSV data
├── tests/
│   ├── python/                  # Python unit tests
│   ├── native/                  # C unit tests
│   └── integration/             # End-to-end tests
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
│   ├── init_db.py
│   └── run_app.bat
├── assets/
│   ├── icons/
│   └── fonts/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Development Notes

- **Native modules** are optional. If the C DLLs in `native/build/` are absent, MEDICARE automatically falls back to pure Python implementations with no loss of functionality.
- **Patient PII** must never be written to log files. All log calls must use non-identifying event types only.
- **Database** uses SQLite with `PRAGMA foreign_keys = ON`. All queries are parameterised to prevent injection.
- **Configuration** is loaded from `config.json` at the project root (auto-generated on first run).

---

## License

Copyright © 2024 MEDICARE Project Contributors.  
This software is provided for educational and research purposes only.  
All rights reserved. See `docs/LICENSE.txt` for full terms.

---

*MEDICARE v1.0.0 — Not for clinical use.*
