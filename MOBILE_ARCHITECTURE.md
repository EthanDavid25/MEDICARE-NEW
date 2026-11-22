# MEDICARE Android Mobile Architecture Specification

## 1. Executive Overview

MEDICARE Mobile extends the authoritative clinical triage engine of the MEDICARE Windows Desktop system to Android mobile devices. It is designed specifically for the healthcare landscape of Maharashtra, India, providing dual-mode operational capability:
1. **Network Connected Mode**: High-performance HTTP/REST communication with the FastAPI backend (`backend/main.py`) powered by the Python core.
2. **Autonomous Offline Mode**: Standalone clinical decision support running entirely on-device via the TypeScript `OfflineTriageEngine` and `OfflineQuestionEngine` without requiring Wi-Fi, mobile data, or a SIM card.

---

## 2. System Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                            MEDICARE MOBILE CLIENT                               |
|                                                                                 |
|  +---------------------------------------------------------------------------+  |
|  |                            UI SCREEN LAYER                                |  |
|  |  Splash • Onboarding • Registration • Dashboard • SymptomAssessment       |  |
|  |  AssessmentResults • HospitalFinder • History • DoctorHandover • Settings |  |
|  +-------------------------------------+-------------------------------------+  |
|                                        |                                        |
|  +-------------------------------------v-------------------------------------+  |
|  |                   UNIFIED API CLIENT (src/api/client.ts)                  |  |
|  |         Auto-detects backend connectivity with graceful fallback          |  |
|  +-------------------+-----------------------------------+-------------------+  |
|                      | (Online)                          | (Offline)            |
|                      v                                   v                      |
|  +-----------------------------------+   +-----------------------------------+  |
|  |        FASTAPI REST BACKEND       |   |       OFFLINE CLINICAL ENGINE     |  |
|  |  • /api/assessment/evaluate       |   |  • OfflineTriageEngine            |  |
|  |  • /api/assessment/next-question  |   |  • OfflineQuestionEngine          |  |
|  |  • /api/hospitals/nearby          |   |  • Bundled Datasets (81 symptoms, |  |
|  |  • /api/patients                  |   |    28 questions, 22 rules,        |  |
|  |  • /api/reports/handover          |   |    14 verified MH hospitals)      |  |
|  +-----------------------------------+   +-----------------------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 3. Core Architectural Subsystems

### A. Authoritative Clinical Engine Portability
The mobile system achieves 100% equivalence with the desktop system:
- **Chief Symptom Dictionary**: 81 clinical symptoms mapped to cardiovascular, respiratory, gastrointestinal, neurological, and musculoskeletal categories.
- **Adaptive Question Engine**: 28 clinical follow-up questions strictly constrained to **≤ 7 words per prompt** for maximum clarity and cognitive ease.
- **Triage Urgency Rules**: 22 medical inference rules mapping findings to 4 standardized clinical urgency tiers:
  * **Category 1 (Emergency)**: Red alert. Immediate emergency room evaluation; 112/108 dispatch.
  * **Category 2 (Urgent)**: Amber alert. Prompt evaluation within 4–12 hours.
  * **Category 3 (Routine)**: Blue alert. Primary care appointment within 24–48 hours.
  * **Category 4 (Self-Care)**: Green alert. Supportive home care and monitoring.

### B. India-Specific Customizations
- **Mobile Number Validation**: Enforces Indian mobile formatting rules: 10 digits starting with 6, 7, 8, or 9; standardizes output as `+91-XXXXX-XXXXX`.
- **Maharashtra Healthcare Directory**: 14 verified tertiary and emergency facilities across Mumbai, Pune, Thane, Navi Mumbai, Nashik, and Nagpur.
- **National Emergency Integration**: Direct calling integration for Indian helplines:
  * `112`: National Emergency (All-in-One)
  * `108`: Emergency Medical Ambulance (Maharashtra & National)
  * `102`: Free Maternity and Child Ambulance
  * `104`: 24/7 State Medical Advice & Health Helpline

### C. Doctor Handover Subsystem
Structured clinical handover reports are generated following medical triage standards:
- Demographics (Name, Age, Sex, Contact, Emergency Contact, Blood Group, Chronic History)
- Triage Urgency Category & Severity Score (1-10)
- Chief Complaint & Pertinent Findings
- Recommended Immediate Action & Clinical Rationale
- ReportLab PDF export when connected, and instant system share sheet when offline.

---

## 4. Security & Offline Storage Architecture

- **Local Persistence**: `AsyncStorageWrapper` provides encrypted/sandboxed key-value storage for patient demographics, assessment history, and cached facilities.
- **No Remote Leakage**: All health assessments are stored strictly on-device unless explicitly exported by the user.
- **SIM-Free Operation**: App functions smoothly on Wi-Fi-only tablets or offline devices without telephony hardware.
