/**
 * MEDICARE Unified API Client with Automatic Offline Fallback.
 * Connects to the authoritative FastAPI backend when available.
 * Transparently falls back to the local OfflineTriageEngine when offline or unreachable.
 */
import Constants from "expo-constants";
import {
  Symptom,
  SymptomEvaluationInput,
  FollowupQuestion,
  TriageEvaluationResponse,
  HealthcareFacility,
  PatientProfile,
  HandoverReportResponse
} from "../types";
import { OfflineTriageEngine, OfflineQuestionEngine, QuestionSessionState } from "../clinical/offlineEngine";
import { BUNDLED_SYMPTOMS, BUNDLED_FACILITIES } from "../clinical/datasets";
import { StorageService } from "../storage/asyncStorage";

// Determine API Base URL:
// 10.0.2.2 is the Android Emulator alias for Host loopback;
// Configurable via app.json or environment.
const DEFAULT_API_URL = Constants.expoConfig?.extra?.apiUrl || "http://10.0.2.2:8000";

let _isOfflineMode = false;
let _offlineQuestionSession: QuestionSessionState | null = null;

export class ApiClient {
  private static baseUrl = DEFAULT_API_URL;

  public static setBaseUrl(url: string) {
    this.baseUrl = url;
  }

  public static isOffline(): boolean {
    return _isOfflineMode;
  }

  public static setOfflineMode(offline: boolean) {
    _isOfflineMode = offline;
  }

  // --- Health Check ---
  public static async checkHealth(): Promise<{ online: boolean; message: string }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.baseUrl}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        _isOfflineMode = false;
        return { online: true, message: "Connected to MEDICARE Clinical Server" };
      }
    } catch {
      _isOfflineMode = true;
    }
    return { online: false, message: "Running in Offline Clinical Mode (100% Local)" };
  }

  // --- Symptoms List ---
  public static async getSymptoms(): Promise<Symptom[]> {
    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2500);
        const res = await fetch(`${this.baseUrl}/api/assessment/symptoms`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          return await res.json();
        }
      } catch {
        _isOfflineMode = true;
      }
    }
    // Offline fallback to bundled symptoms
    return BUNDLED_SYMPTOMS as unknown as Symptom[];
  }

  // --- Start Assessment ---
  public static async startAssessment(symptoms: SymptomEvaluationInput[]): Promise<{
    session_id: string;
    total_budget: number;
    first_question: FollowupQuestion | null;
  }> {
    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${this.baseUrl}/api/assessment/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symptoms }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          return {
            session_id: data.session_id,
            total_budget: data.total_questions_budget,
            first_question: data.first_question
          };
        }
      } catch {
        _isOfflineMode = true;
      }
    }

    // Authoritative Offline Engine Fallback
    _offlineQuestionSession = OfflineQuestionEngine.createSession(symptoms);
    const firstQ = OfflineQuestionEngine.getNextQuestion(_offlineQuestionSession);
    return {
      session_id: _offlineQuestionSession.sessionId,
      total_budget: _offlineQuestionSession.maxQuestions,
      first_question: firstQ
    };
  }

  // --- Next Adaptive Question ---
  public static async getNextQuestion(
    sessionId: string,
    symptoms: SymptomEvaluationInput[],
    answersSoFar: Record<string, string>,
    currentQuestionId?: string,
    currentAnswer?: string
  ): Promise<{
    question: FollowupQuestion | null;
    question_number: number;
    is_complete: boolean;
  }> {
    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${this.baseUrl}/api/assessment/next-question`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            symptoms,
            answers_so_far: answersSoFar,
            current_question_id: currentQuestionId,
            current_answer: currentAnswer
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          return {
            question: data.question,
            question_number: data.question_number,
            is_complete: data.is_complete
          };
        }
      } catch {
        _isOfflineMode = true;
      }
    }

    // Authoritative Offline Engine Fallback
    if (!_offlineQuestionSession) {
      _offlineQuestionSession = OfflineQuestionEngine.createSession(symptoms, sessionId);
    }
    const combinedAnswers = { ...answersSoFar };
    if (currentQuestionId && currentAnswer) {
      combinedAnswers[currentQuestionId] = currentAnswer;
    }
    for (const [qid, ans] of Object.entries(combinedAnswers)) {
      OfflineQuestionEngine.recordAnswer(_offlineQuestionSession, qid, ans);
    }
    const nextQ = OfflineQuestionEngine.getNextQuestion(_offlineQuestionSession);
    const count = Object.keys(combinedAnswers).length;
    return {
      question: nextQ,
      question_number: count + (nextQ ? 1 : 0),
      is_complete: nextQ === null
    };
  }

  // --- Triage Evaluation ---
  public static async evaluateAssessment(
    sessionId: string,
    symptoms: SymptomEvaluationInput[],
    followupAnswers: Record<string, string>,
    riskFactors: string[] = []
  ): Promise<TriageEvaluationResponse> {
    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000);
        const res = await fetch(`${this.baseUrl}/api/assessment/evaluate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            symptoms,
            followup_answers: followupAnswers,
            risk_factors: riskFactors
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          return await res.json();
        }
      } catch {
        _isOfflineMode = true;
      }
    }

    // Authoritative Offline Triage Engine Fallback
    return OfflineTriageEngine.assess(symptoms, followupAnswers, riskFactors, sessionId);
  }

  // --- Nearby Hospitals ---
  public static async getNearbyHospitals(params: {
    latitude?: number;
    longitude?: number;
    locality?: string;
    radiusKm?: number;
    emergencyOnly?: boolean;
  }): Promise<HealthcareFacility[]> {
    if (!_isOfflineMode) {
      try {
        const q = new URLSearchParams();
        if (params.latitude !== undefined) q.append("latitude", params.latitude.toString());
        if (params.longitude !== undefined) q.append("longitude", params.longitude.toString());
        if (params.locality) q.append("locality", params.locality);
        if (params.radiusKm) q.append("radius_km", params.radiusKm.toString());
        if (params.emergencyOnly) q.append("emergency_only", "true");

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${this.baseUrl}/api/hospitals/nearby?${q.toString()}`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          // Cache for offline access
          await StorageService.cacheFacilities(data.facilities);
          return data.facilities;
        }
      } catch {
        _isOfflineMode = true;
      }
    }

    // Offline Hospital Search using bundled facilities + Haversine distance
    const facilities: HealthcareFacility[] = (BUNDLED_FACILITIES as unknown) as HealthcareFacility[];
    const results: HealthcareFacility[] = [];

    const searchLat = params.latitude;
    const searchLon = params.longitude;

    for (const f of facilities) {
      if (params.emergencyOnly && !f.has_emergency) continue;

      let dist: number | undefined = undefined;
      if (searchLat !== undefined && searchLon !== undefined) {
        dist = this.haversineKm(searchLat, searchLon, f.latitude, f.longitude);
      }

      if (params.locality) {
        const query = params.locality.toLowerCase().trim();
        const match =
          f.name.toLowerCase().includes(query) ||
          (f.locality && f.locality.toLowerCase().includes(query)) ||
          f.city.toLowerCase().includes(query) ||
          (f.district && f.district.toLowerCase().includes(query));
        if (!match && (dist === undefined || dist > (params.radiusKm || 50))) {
          continue;
        }
      }

      results.push({
        ...f,
        distance_km: dist !== undefined ? Math.round(dist * 10) / 10 : undefined
      });
    }

    if (searchLat !== undefined && searchLon !== undefined) {
      results.sort((a, b) => (a.distance_km || 999) - (b.distance_km || 999));
    }

    return results;
  }

  // --- Patient Registration ---
  public static async registerPatient(profile: PatientProfile): Promise<PatientProfile> {
    // Save locally first
    await StorageService.savePatientProfile(profile);

    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${this.baseUrl}/api/patients`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(profile),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          const saved = await res.json();
          await StorageService.savePatientProfile(saved);
          return saved;
        }
      } catch {
        _isOfflineMode = true;
      }
    }
    return profile;
  }

  // --- Handover Report Generation ---
  public static async generateHandoverPdf(
    sessionId: string,
    triageResult: TriageEvaluationResponse,
    patientId: number = 1
  ): Promise<HandoverReportResponse> {
    if (!_isOfflineMode) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000);
        const res = await fetch(`${this.baseUrl}/api/reports/handover`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            patient_id: patientId,
            triage_result: triageResult
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          return await res.json();
        }
      } catch {
        _isOfflineMode = true;
      }
    }

    // Local Handover Reference
    return {
      session_id: sessionId,
      pdf_filename: `Handover_${sessionId}.pdf`,
      download_url: "",
      created_at: new Date().toISOString()
    };
  }

  public static async isBackendOnline(): Promise<boolean> {
    const health = await this.checkHealth();
    return health.online;
  }

  /**
   * Alias: generateHandoverReport — convenience wrapper used by DoctorHandoverScreen.
   * Delegates to generateHandoverPdf with the session_id from the payload.
   */
  public static async generateHandoverReport(payload: {
    assessment_id?: string;
    session_id?: string;
    [key: string]: any;
  }): Promise<HandoverReportResponse> {
    const sessionId = payload.session_id || payload.assessment_id || "unknown";
    return this.generateHandoverPdf(sessionId, payload as unknown as TriageEvaluationResponse);
  }

  private static haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const R = 6371; // Earth radius in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }
}

export const apiClient = ApiClient;
