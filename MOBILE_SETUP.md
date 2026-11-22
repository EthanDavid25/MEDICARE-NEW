# MEDICARE Mobile Developer & Setup Guide

This guide describes how to run, test, and develop the MEDICARE Android mobile application.

---

## 1. Prerequisites

- **Node.js**: v18.x or newer (Tested on v26.13.1)
- **Python**: 3.11.x (for running the FastAPI clinical backend)
- **Expo Go** or an Android physical phone / emulator (Android 7.0+ / API 24+)

---

## 2. Directory Structure

```
MEDICARE_OFFLINE/
├── backend/                  # FastAPI authoritative REST backend
│   ├── api/                  # Endpoints (assessment, hospitals, patients, reports, sync)
│   ├── schemas/              # Pydantic v2 data models
│   ├── tests/                # Automated backend unit tests (10/10 PASS)
│   └── main.py               # FastAPI entry point
├── mobile/                   # React Native + Expo mobile application
│   ├── android/              # Native Android wrapper and manifest
│   ├── dist/                 # Generated debug APK and bundles
│   ├── src/
│   │   ├── api/              # Unified API client with offline fallback
│   │   ├── clinical/         # TypeScript offline clinical engine & bundled datasets
│   │   ├── components/       # UI components (Header, Button, Card, PainSlider, etc.)
│   │   ├── navigation/       # Bottom tabs & Root stack navigation
│   │   ├── screens/          # All 10 application screens
│   │   ├── storage/          # Local device storage wrapper
│   │   └── theme/            # Healthcare navy & white design system
│   ├── tests/                # Automated mobile test runner (10/10 PASS)
│   ├── App.tsx               # Root mobile component
│   └── app.json              # Expo application configuration
└── shared/
    └── types.ts              # TypeScript contracts matching backend models
```

---

## 3. Starting the Backend API

To start the authoritative backend server:

```powershell
cd MEDICARE_OFFLINE
$env:PYTHONPATH="."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API documentation is interactively accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 4. Running the Mobile Application

### Step A: Install Dependencies
```powershell
cd MEDICARE_OFFLINE/mobile
npm install
```

### Step B: Start Expo Development Server
```powershell
npm start
```
Scan the displayed QR code with the **Expo Go** app on your Android phone, or press `a` to launch on a connected Android emulator.

---

## 5. Standalone APK Installation & Wi-Fi Testing

A standalone debug APK is pre-packaged at:
```
MEDICARE_OFFLINE/dist/medicare-debug.apk
MEDICARE_OFFLINE/mobile/dist/medicare-debug.apk
```

### Installing on an Android Device:
1. Transfer `medicare-debug.apk` to your phone via USB cable, Google Drive, or local HTTP server.
2. Open the file on your device and tap **Install**.
3. (If prompted, enable *"Install from Unknown Sources"* for your file manager).
4. Launch **MEDICARE** directly.

### Wi-Fi-Only & Offline Testing:
1. The app works 100% offline without cellular reception or mobile data.
2. Turn on Airplane Mode with Wi-Fi disabled to test autonomous clinical triage.
3. The app will immediately show the offline indicator and route all clinical assessments to the local TypeScript inference engine with zero delay.
