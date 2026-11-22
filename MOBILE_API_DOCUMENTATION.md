# MEDICARE Backend REST API Documentation

## 1. Overview
The MEDICARE FastAPI backend exposes the authoritative Python clinical triage engine, healthcare directory services, patient profile management, and ReportLab PDF handover generation.

Base URL: `http://localhost:8000/api`

---

## 2. API Endpoints

### 1. Health Check
- **`GET /health`**
- **Response `200 OK`**:
  ```json
  {
    "status": "online",
    "version": "1.0.0",
    "clinical_engine": "v2.1.0-compact",
    "environment": "production"
  }
  ```

---

### 2. Clinical Assessment & Triage

#### A. Get All Symptoms
- **`GET /api/assessment/symptoms`**
- Returns all 81 symptoms with unique IDs, names, and medical categories.

#### B. Start New Assessment Session
- **`POST /api/assessment/start`**
- **Request Body**:
  ```json
  {
    "patient_id": 1,
    "chief_symptom": "chest_pain"
  }
  ```
- **Response**: Session ID, symptom details, and first adaptive question.

#### C. Get Next Adaptive Question
- **`POST /api/assessment/next-question`**
- **Request Body**:
  ```json
  {
    "chief_symptom": "chest_pain",
    "answered_questions": {
      "QID_CHEST_RADIATION": "YES"
    }
  }
  ```
- **Response `200 OK`**: Next dynamic question (≤ 7 words) or `null` if sufficient clinical data has been gathered.

#### D. Evaluate Full Triage Assessment
- **`POST /api/assessment/evaluate`**
- **Request Body**:
  ```json
  {
    "patient_age": 55,
    "patient_gender": "male",
    "chief_symptom": "chest_pain",
    "pain_severity": 9,
    "duration_hours": 2,
    "progression": "worsening",
    "warning_signs": ["radiating_to_arm"],
    "answers": {
      "QID_CHEST_RADIATION": "YES"
    }
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "assessment_id": "SES_A1B2C3D4",
    "category": "emergency",
    "severity_score": 9,
    "chief_symptom": "chest_pain",
    "recommended_action": "Seek immediate emergency medical attention or call 112 / 108.",
    "explanation": "Acute severe chest pain with radiation to arm indicative of possible acute coronary syndrome.",
    "matched_rules": [
      {
        "rule_id": "RULE_CHEST_ACS",
        "description": "Acute chest pain radiating to arm"
      }
    ],
    "timestamp": "2026-11-22T14:20:00Z"
  }
  ```

---

### 3. Maharashtra Healthcare Directory

#### A. Nearby Hospital Search
- **`GET /api/hospitals/nearby?lat=19.0033&lon=72.8427&radius_km=50&emergency_only=false`**
- Calculates distances using the Haversine formula and returns sorted facilities with travel metadata, 24/7 emergency status, and contact numbers.

#### B. Hospital Facility Details
- **`GET /api/hospitals/{hospital_id}`**
- Returns complete facility profiles (beds, ICU, trauma level, address).

---

### 4. Patient Registration & India Validation

- **`POST /api/patients`**
- Validates Indian phone numbers (+91, 10 digits starting with 6, 7, 8, or 9).
- **Request Body**:
  ```json
  {
    "name": "Ramesh Kulkarni",
    "age": 48,
    "gender": "male",
    "phone": "9820012345",
    "emergency_contact": "9820098765",
    "blood_group": "B+",
    "medical_conditions": ["Hypertension"]
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "patient_id": 2,
    "name": "Ramesh Kulkarni",
    "phone": "+91-98200-12345",
    "created_at": "2026-11-22T14:20:00Z"
  }
  ```

---

### 5. Doctor Handover & Reports

- **`POST /api/reports/handover`**
- Compiles the clinical handover report into a ReportLab PDF with structured headers, urgency category bands, and findings.
- **`GET /api/reports/download/{filename}`**
- Downloads the generated PDF document.

---

### 6. Offline Synchronization Bundle

- **`GET /api/sync/bundle`**
- Returns a complete JSON bundle of all 81 symptoms, 28 questions, 22 rules, 40 warning signs, and 14 hospitals for local caching.
