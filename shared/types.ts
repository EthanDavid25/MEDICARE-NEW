/**
 * MEDICARE Shared Types & API Contracts
 * Canonical interfaces shared between the Python backend and React Native mobile application.
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
  name: string;
  category: string;
  description?: string;
  default_severity?: number;
  body_system?: string;
}

export interface SymptomEvaluationInput {
  code: string;
  name: string;
  severity: number;
  duration_value?: number;
  duration_unit?: string;
  progression?: "improving" | "stable" | "worsening";
  notes?: string;
}

export interface QuestionOption {
  code: string;
  text: string;
  triggers_emergency?: boolean;
}

export interface FollowupQuestion {
  question_id: string;
  symptom_code: string;
  question_text: string;
  options: QuestionOption[];
  is_required: boolean;
  priority: number;
  category?: string;
  branching_logic?: Record<string, string>;
}

export interface AssessmentStartRequest {
  patient_id?: number;
  symptoms: SymptomEvaluationInput[];
}

export interface AssessmentStartResponse {
  session_id: string;
  total_symptoms: number;
  total_questions_budget: number;
  first_question: FollowupQuestion | null;
}

export interface NextQuestionRequest {
  session_id: string;
  symptoms: SymptomEvaluationInput[];
  answers_so_far: Record<string, string>;
  current_question_id?: string;
  current_answer?: string;
}

export interface NextQuestionResponse {
  question: FollowupQuestion | null;
  question_number: number;
  total_estimated: number;
  is_complete: boolean;
}

export interface TriageEvaluationRequest {
  session_id?: string;
  patient_id?: number;
  symptoms: SymptomEvaluationInput[];
  followup_answers: Record<string, string>;
  risk_factors?: string[];
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

export interface HealthcareFacility {
  id: string;
  name: string;
  facility_type: string;
  locality: string;
  city: string;
  district: string;
  state: string;
  pincode: string;
  latitude: number;
  longitude: number;
  phone: string;
  emergency_helpline?: string;
  has_emergency: boolean;
  has_icu: boolean;
  has_trauma_care: boolean;
  beds_count?: number;
  ownership: "Government" | "Municipal" | "Trust" | "Private";
  distance_km?: number;
}

export interface PatientProfile {
  id?: number;
  display_name: string;
  phone_number: string;
  date_of_birth?: string;
  age?: number;
  biological_sex?: "male" | "female" | "other";
  blood_group?: string;
  emergency_contact?: string;
  known_allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  preferred_language?: string;
}

export interface HandoverReportResponse {
  session_id: string;
  pdf_filename: string;
  download_url: string;
  created_at: string;
}
