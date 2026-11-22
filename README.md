# MEDICARE — Medical Symptoms Triage Advisor

> ⚕️ An offline-first cross-platform application for structured medical symptom triage and nearby healthcare discovery.

---

## ⚠️ Medical Disclaimer

> **THIS APPLICATION IS NOT FOR CLINICAL USE.**
>
> MEDICARE is a decision-support and educational tool only. It does **not** provide medical diagnoses, replace professional medical advice, or constitute a validated clinical system. It has **not** been endorsed by the World Health Organization, any national health authority, or any clinical body.
>
> Always consult a qualified healthcare professional for any medical concern. In a life-threatening emergency, call your local emergency services immediately (e.g., **911** in the USA, **999** in the UK, **112** in the EU, **102** in India).
>
> Triage recommendations produced by this application are based on generalised rule-based logic and are intended solely to help users organise and communicate their symptoms — not to substitute clinical judgement.

---

## Overview

MEDICARE is a cross-platform desktop application built with **Python**, **Kivy**, and native **C modules**. It runs fully offline and enables users to:

- Log and track symptoms with severity, duration, and progression
- Receive structured triage guidance (urgency categories 1–4)
- Answer adaptive follow-up questions based on symptom trajectory
- Manage a local encrypted patient profile
- Find nearby healthcare facilities (live via Google Maps, or offline directory)
- Generate printable doctor handover PDF summaries
- Review symptom history and progression trends

All patient data is stored **locally on-device** in an encrypted SQLite database. No medical data is ever transmitted to any server.

---

## Features

| Feature | Description |
|---------|-------------|
| 🩺 Symptom Logger | Capture symptoms with severity (1–10 slider), duration, and worsening/stable/improving trajectory |
| 🚦 Triage Engine | Rule-based urgency categorisation: Emergency → Early Consultation → Routine → Insufficient |
| 📋 Patient Profiles | Locally encrypted patient records (name, DOB, blood group, allergies, medications) |
| ❓ Adaptive Follow-ups | Symptom-specific and trajectory-aware follow-up questions; emergency red-flags always shown |
| 🏥 Facility Finder | Live nearby hospital search via Google Maps API; offline CSV directory fallback |
| 📈 History & Trends | Symptom progression tracking over time |
| 📄 PDF Reports | Generate printable assessment summaries for doctor handover (ReportLab) |
| 🔒 Security | Local field-level encryption (cryptography / Fernet) |
| 🌐 Offline First | 100% air-gapped capable; Google Maps is optional and gracefully degraded |
| 🖥️ Windows & Android | Shared Python/Kivy codebase; PyInstaller (Windows) + Buildozer (Android) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI / Application | Python 3.11+ · Kivy 2.3+ |
| Triage Engine (native) | C99 · ctypes bridge (Python fallbacks included) |
| Offline Map Engine (native) | C11 (Tile math, 2D Spatial Grid, A* routing, LRU tile cache) |
| PDF Generation | ReportLab |
| Database | SQLite3 (stdlib) |
| Security | cryptography (Fernet) |
| Maps Integration | Google Places API (New) · Geocoding API |
| Windows Packaging | PyInstaller 6+ |
| Android Packaging | Buildozer (Linux/WSL required) |

---

## Project Structure

```
MEDICARE_OFFLINE/
├── app/
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── logger.py              # Logging setup
│   │   ├── database.py            # SQLite database layer
│   │   ├── native_loader.py       # C DLL loader with Python fallbacks
│   │   ├── app_controller.py      # Central application controller
│   │   └── fallback/              # Pure-Python fallback implementations
│   ├── ui/
│   │   ├── app.py                 # Kivy app shell (sidebar + ScreenManager)
│   │   ├── screens.py             # All 12 application screens
│   │   ├── components.py          # Reusable widgets (WrappedLabel, CardBox, etc.)
│   │   └── theme.py               # Color palette and layout helpers
│   ├── healthcare/
│   │   ├── location_service.py    # Location resolution + facility search orchestration
│   │   ├── maps_service.py        # Google Maps Places API + Geocoding integration
│   │   ├── offline_map_service.py # Spatial grid querying & offline hospital routing
│   │   └── native_map_loader.py   # C map engine ctypes bindings & fallback
│   ├── datasets/                  # Medical dataset loader (symptoms, rules, questions)
│   ├── triage/                    # Triage engine (Python side)
│   ├── patients/                  # Patient profile management
│   ├── history/                   # Symptom history service
│   ├── reports/                   # PDF doctor handover generation
│   └── security/                  # Field encryption utilities
├── native/
│   ├── include/                   # C header files (medicare_geo_types.h, medicare_map_engine.h)
│   ├── src/                       # C source files (map_tile_engine, geo_engine, routing_engine, validator)
│   └── build/                     # Compiled DLLs & build scripts (build_map_engine.bat, CMakeLists.txt)
├── data/
│   ├── medical/                   # JSON clinical & technical geographic reference datasets
│   └── healthcare/                # Local facility CSV directory
├── tests/
│   ├── python/                    # Python unit tests (27 unit tests across core, UI, and map engines)
│   └── integration/               # End-to-end tests
├── scripts/
│   ├── benchmark_geo_engine.py    # Native vs Python geographic algorithm benchmark suite
│   ├── capture_all_screens.py     # Screenshot all 12 screens
│   ├── verify_demo_readiness.py   # Pre-demo audit checks
│   ├── push_to_github.bat         # GitHub publish launcher
│   └── run_app.bat                # Windows convenience launcher
├── docs/                          # Architecture guides
├── assets/                        # Icons, fonts
├── .env.example                   # API key configuration template
├── requirements.txt               # Python dependencies
├── medicare.spec                  # PyInstaller build configuration
├── buildozer.spec                 # Android/Buildozer configuration
└── main.py                        # Root entry point
```

---

## Installation

### Prerequisites

- **Python 3.11+** (tested on Python 3.11.9)
- **Windows 10/11** (primary platform; Linux supported for development)
- **1 GB RAM** minimum
- **1366×768** display minimum

### 1. Clone the repository

```bash
git clone https://github.com/EthanDavid25/MEDICARE-NEW.git
cd MEDICARE-NEW
```

### 2. Create a virtual environment (recommended)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Google Maps (optional)

Copy the template and add your API key:

```powershell
Copy-Item .env.example .env
# Edit .env and replace "your_api_key_here" with your real key
```

See [Google Maps API Setup](#google-maps-api-setup) below. Without this, MEDICARE uses the local offline facility directory.

### 5. Launch the application

```powershell
python main.py
```

Or use the convenience launcher:

```powershell
scripts\run_app.bat
```

---

## Windows Executable

A pre-built Windows executable is available in `dist\MEDICARE\MEDICARE.exe`.

To rebuild the executable from source:

```powershell
# Set KIVY_HOME to avoid permission errors
$env:KIVY_HOME = "$pwd\.kivy_home"

# Rebuild
python -m PyInstaller --clean --noconfirm medicare.spec
```

The rebuilt executable will be at `dist\MEDICARE\MEDICARE.exe`.

---

## Android Build

> **Note:** Android APK generation is not possible on Windows natively. It requires Linux or WSL2.

On a Linux machine with buildozer installed:

```bash
# Install buildozer
pip install buildozer

# Install Android SDK/NDK dependencies
sudo apt-get install -y build-essential git python3-dev ...

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release
```

The `buildozer.spec` is pre-configured for MEDICARE. The resulting APK will be in `bin/`.

---

## Running Tests

```powershell
$env:KIVY_HOME = "$pwd\.kivy_home"
python -m unittest discover -s tests/python -p "test_*.py" -v
```

Expected output: **17 tests pass** (10 core + 7 UI/location).

---

## Google Maps API Setup

MEDICARE integrates with the **Google Places API (New)** and **Geocoding API** to provide live nearby healthcare facility search.

### Setup Steps

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable these APIs:
   - **Places API (New)** — for nearby hospital/clinic search
   - **Geocoding API** — for manual address → coordinates
4. Create an API key under **APIs & Services → Credentials**
5. **Restrict your key:**
   - Application restrictions: Windows apps or allowed IP addresses
   - API restrictions: Select only "Places API" and "Geocoding API"
6. Enable billing (required for Places API; Google provides a free monthly credit)
7. Copy your key to `.env`:

```
GOOGLE_MAPS_API_KEY=AIzaSy...your_key_here
```

### Security Notes

- **Never commit your API key to version control.** `.env` is in `.gitignore`.
- The key is read from the `GOOGLE_MAPS_API_KEY` environment variable at runtime.
- Only geographic coordinates (lat/lon) are sent to Google — no symptoms, patient data or medical history is ever transmitted.
- The key is a client-side key. Apply API and application restrictions in the Google Cloud Console to limit exposure.
- Rotate the key immediately if compromised.

### Without a Key

MEDICARE works fully without a Google Maps API key. The Healthcare Directory will display the local offline facility directory instead of live Google Maps results. All other features remain fully functional.

---

## Urgency Categories

| Category | Label | Description |
|----------|-------|-------------|
| 1 | Emergency Care | Seek immediate emergency department attention |
| 2 | Early Consultation | Consult a doctor within 24–48 hours |
| 3 | Routine Healthcare | Schedule a routine appointment |
| 4 | Insufficient Information | Unable to triage; answer more questions |

Emergency safety guidance is always shown, even when offline or when location permission is denied.

---

## Privacy

- All patient data is stored locally in an encrypted SQLite database.
- No patient symptoms, history, or medical data is transmitted to any server.
- Google Maps receives only geographic coordinates for facility search.
- Location is only requested when the user explicitly clicks "Use Device Location".
- Location can be cleared at any time from the Healthcare Directory screen.

---

## Known Limitations

- **Android:** APK build requires Linux/WSL2 with buildozer. Not tested on Android hardware.
- **Native C modules:** Optional; pure Python fallbacks are used if DLLs are absent.
- **Google Maps live search:** Requires a configured API key and internet access.
- **Location accuracy:** Device location uses IP-based geolocation (approximate city level).
- **Facility data:** Offline directory contains demonstration data only. Live results come from Google Maps.

---

## Development Status

| Component | Status |
|-----------|--------|
| Core triage engine | ✅ Complete |
| All 12 UI screens | ✅ Complete |
| Patient profile encryption | ✅ Complete |
| PDF doctor handover | ✅ Complete |
| Symptom history tracking | ✅ Complete |
| Google Maps integration (structure) | ✅ Complete |
| Google Maps live testing | ⚠️ Requires API key configuration |
| Android APK | ⚠️ Requires Linux/WSL2 |
| Native C modules | ⚠️ Optional; Python fallbacks active |

---

## License

Copyright © 2024–2026 MEDICARE Project Contributors.  
This software is provided for educational and research purposes only.  
Not for clinical use. All rights reserved.

---

*MEDICARE v1.0.0 — Not for clinical use. Not clinically validated. Not endorsed by any health authority.*
