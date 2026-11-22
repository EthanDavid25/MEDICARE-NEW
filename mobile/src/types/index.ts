/**
 * MEDICARE Shared Types & API Contracts (Mobile Local Copy)
 */

export type UrgencyCategory = 1 | 2 | 3 | 4;

export interface UrgencyMeta {
  category: UrgencyCategory;
  title: string;
  shortLabel: string;
  colorHex: string;
  bgHex: string;
}

export interface Symptom {
  code: string;
  id?: string;
  name: string;
  category: string;
  description?: string;
  default_severity?: number;
  body_system?: string;
}

export type SymptomOption = Symptom;

export interface SymptomEvaluationInput {
  code: string;
  name: string;
  severity: number;
  duration_value?: number;
  duration_unit?: string;
  progression?: "improving" | "stable" | "unchanged" | "worsening";
  notes?: string;
}

export interface QuestionOption {
  code?: string;
  value?: any;
  text?: string;
  label?: string;
  triggers_emergency?: boolean;
}

export interface FollowupQuestion {
  question_id?: string;
  id?: string;
  symptom_code?: string;
  symptom_codes?: string[];
  question_text?: string;
  prompt?: string;
  options: QuestionOption[];
  is_required: boolean;
  priority?: number;
  category?: string;
  branching_logic?: Record<string, string>;
}

export type FollowUpQuestion = FollowupQuestion;

export interface HealthcareFacility {
  id: string;
  name: string;
  facility_type?: string;
  type?: string;
  locality?: string;
  city: string;
  district?: string;
  state?: string;
  pincode?: string;
  latitude: number;
  longitude: number;
  phone: string;
  emergency_helpline?: string;
  has_emergency: boolean;
  has_icu?: boolean;
  has_trauma_care?: boolean;
  beds_count?: number;
  ownership?: string;
  tier?: string;
  address?: string;
  capabilities?: string[];
  distance_km?: number;
}

export type HospitalFacility = HealthcareFacility;

export interface PatientProfile {
  id?: number;
  display_name?: string;
  name?: string;
  phone_number?: string;
  phone?: string;
  age?: number;
  gender?: "male" | "female" | "other" | string;
  biological_sex?: "male" | "female" | "other";
  blood_group?: string;
  emergency_contact?: string;
  medical_conditions?: string[];
  chronic_conditions?: string;
}

export interface AssessmentResult {
  assessment_id: string;
  session_id?: string;
  category: string;
  urgency_category?: number;
  severity_score: number;
  chief_symptom: string;
  recommended_action: string;
  explanation: string;
  matched_rules?: any[];
  missing_critical_info?: string[];
  timestamp: string;
  completed_at?: string;
}

export interface TriageAssessmentInput {
  patient_age: number;
  patient_gender: string;
  chief_symptom: string;
  pain_severity: number;
  duration_hours: number;
  progression: "improving" | "unchanged" | "worsening";
  warning_signs: string[];
  vital_signs?: Record<string, any>;
  medical_history?: string[];
  answers: Record<string, any>;
}

export interface HandoverReportResponse {
  session_id: string;
  pdf_filename: string;
  download_url: string;
  created_at: string;
}

export interface TriageEvaluationResponse {
  session_id: string;
  urgency_category: UrgencyCategory;
  urgency_label: string;
  started_at: string;
  completed_at: string;
  severity_score: number;
  progression_trend: string;
  emergency_override: boolean;
  warning_signs_found: string[];
  rules_triggered: Array<{
    rule_id: string;
    description?: string;
    explanation?: string;
    urgency_category?: number;
  }>;
  contradictions: string[];
  missing_critical_data: string[];
  summary_explanation: string;
  detailed_reasoning: string[];
  recommended_next_steps: string[];
  uncertainty_statement: string;
  clinical_limitations: string;
  triage_version: string;
}
