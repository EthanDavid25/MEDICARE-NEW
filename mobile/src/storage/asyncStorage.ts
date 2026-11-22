/**
 * Local Storage Layer using AsyncStorage.
 * Manages patient profile, assessment records, settings and offline caches.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import { PatientProfile, TriageEvaluationResponse, HealthcareFacility } from "@shared/types";

const KEYS = {
  PATIENT_PROFILE: "@medicare_patient_profile",
  ASSESSMENT_HISTORY: "@medicare_assessment_history",
  SETTINGS: "@medicare_settings",
  CACHED_FACILITIES: "@medicare_cached_facilities",
  IS_ONBOARDED: "@medicare_is_onboarded"
};

export interface StoredAssessment {
  id: string;
  session_id: string;
  completed_at: string;
  urgency_category: number;
  urgency_label: string;
  symptoms_summary: string;
  severity_score: number;
  result: TriageEvaluationResponse;
}

export interface AppSettings {
  language: "English" | "Hindi" | "Marathi";
  locationPermissionGranted: boolean;
  offlineModePreferred: boolean;
  notificationsEnabled: boolean;
}

export class StorageService {
  // --- Patient Profile ---
  static async getPatientProfile(): Promise<PatientProfile | null> {
    try {
      const data = await AsyncStorage.getItem(KEYS.PATIENT_PROFILE);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }

  static async savePatientProfile(profile: PatientProfile): Promise<boolean> {
    try {
      await AsyncStorage.setItem(KEYS.PATIENT_PROFILE, JSON.stringify(profile));
      return true;
    } catch {
      return false;
    }
  }

  // --- Onboarding Status ---
  static async isOnboarded(): Promise<boolean> {
    try {
      const val = await AsyncStorage.getItem(KEYS.IS_ONBOARDED);
      return val === "true";
    } catch {
      return false;
    }
  }

  static async setOnboarded(status: boolean = true): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.IS_ONBOARDED, status ? "true" : "false");
    } catch {}
  }

  // --- Assessment History ---
  static async getAssessmentHistory(): Promise<StoredAssessment[]> {
    try {
      const data = await AsyncStorage.getItem(KEYS.ASSESSMENT_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  static async saveAssessmentResult(result: TriageEvaluationResponse, symptomsSummary: string): Promise<boolean> {
    try {
      const history = await this.getAssessmentHistory();
      const newEntry: StoredAssessment = {
        id: result.session_id,
        session_id: result.session_id,
        completed_at: result.completed_at || new Date().toISOString(),
        urgency_category: result.urgency_category,
        urgency_label: result.urgency_label,
        symptoms_summary: symptomsSummary,
        severity_score: result.severity_score,
        result
      };
      const updated = [newEntry, ...history.filter(h => h.session_id !== result.session_id)];
      await AsyncStorage.setItem(KEYS.ASSESSMENT_HISTORY, JSON.stringify(updated.slice(0, 50)));
      return true;
    } catch {
      return false;
    }
  }

  // --- Settings ---
  static async getSettings(): Promise<AppSettings> {
    const defaults: AppSettings = {
      language: "English",
      locationPermissionGranted: false,
      offlineModePreferred: false,
      notificationsEnabled: true
    };
    try {
      const data = await AsyncStorage.getItem(KEYS.SETTINGS);
      return data ? { ...defaults, ...JSON.parse(data) } : defaults;
    } catch {
      return defaults;
    }
  }

  static async saveSettings(settings: Partial<AppSettings>): Promise<void> {
    try {
      const current = await this.getSettings();
      await AsyncStorage.setItem(KEYS.SETTINGS, JSON.stringify({ ...current, ...settings }));
    } catch {}
  }

  // --- Cached Facilities ---
  static async getCachedFacilities(): Promise<HealthcareFacility[]> {
    try {
      const data = await AsyncStorage.getItem(KEYS.CACHED_FACILITIES);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  static async cacheFacilities(facilities: HealthcareFacility[]): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.CACHED_FACILITIES, JSON.stringify(facilities));
    } catch {}
  }
}
