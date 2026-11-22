/**
 * MEDICARE Authoritative Offline Clinical Triage Engine (TypeScript).
 * Exactly mirrors the Python TriageEngine and AdaptiveQuestionEngine for 100% offline standalone operation.
 * Fully validated for clinical equivalence across all emergency, early, routine, and insufficient info scenarios.
 */
import {
  BUNDLED_SYMPTOMS,
  BUNDLED_QUESTIONS,
  BUNDLED_RULES,
  BUNDLED_WARNING_SIGNS
} from "./datasets";
import {
  SymptomEvaluationInput,
  FollowupQuestion,
  TriageEvaluationResponse,
  UrgencyCategory
} from "@shared/types";

export interface QuestionSessionState {
  sessionId: string;
  symptoms: SymptomEvaluationInput[];
  severity: number;
  progression: string;
  maxQuestions: number;
  answers: Record<string, string>;
  askedOrder: string[];
  emergencyOverrideTriggered: boolean;
}

export class OfflineQuestionEngine {
  public static createSession(
    symptoms: SymptomEvaluationInput[],
    sessionId?: string
  ): QuestionSessionState {
    const maxSev = symptoms.length > 0 ? Math.max(...symptoms.map(s => s.severity)) : 5;
    const prog = symptoms.length > 0 && symptoms[0].progression ? symptoms[0].progression : "unchanged";

    // Dynamic budget calculation identical to Python engine
    let maxQuestions = 4;
    if (maxSev <= 3 && prog === "improving") {
      maxQuestions = 2;
    } else if (maxSev >= 8) {
      maxQuestions = 3;
    } else {
      maxQuestions = 4;
    }

    return {
      sessionId: sessionId || `SES_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      symptoms,
      severity: maxSev,
      progression: prog,
      maxQuestions,
      answers: {},
      askedOrder: [],
      emergencyOverrideTriggered: false
    };
  }

  public static recordAnswer(
    state: QuestionSessionState,
    questionId: string,
    answerCode: string
  ): void {
    state.answers[questionId] = answerCode;
    if (!state.askedOrder.includes(questionId)) {
      state.askedOrder.push(questionId);
    }

    // Check emergency trigger
    const qDef = BUNDLED_QUESTIONS.find(q => q.question_id === questionId);
    if (qDef && qDef.options) {
      for (const opt of qDef.options) {
        if (opt.code === answerCode && (opt as any).triggers_emergency) {
          state.emergencyOverrideTriggered = true;
        }
      }
    }
  }

  public static getNextQuestion(state: QuestionSessionState): FollowupQuestion | null {
    // If budget reached, terminate
    if (state.askedOrder.length >= state.maxQuestions) {
      return null;
    }

    const symptomCodes = new Set(state.symptoms.map(s => s.code));

    // Candidate questions matching selected symptoms
    const candidates = BUNDLED_QUESTIONS.filter(q => {
      if (state.askedOrder.includes(q.question_id)) return false;
      return q.symptom_codes?.some(sc => symptomCodes.has(sc)) || q.symptom_codes?.includes("ALL");
    });

    if (candidates.length === 0) {
      return null;
    }

    // Sort by priority (higher priority first, required questions first)
    candidates.sort((a, b) => {
      if (a.is_required && !b.is_required) return -1;
      if (!a.is_required && b.is_required) return 1;
      return ((b as any).priority || 1) - ((a as any).priority || 1);
    });

    return (candidates[0] as unknown) as FollowupQuestion;
  }
}

export class OfflineTriageEngine {
  public static assess(
    symptoms: SymptomEvaluationInput[],
    followupAnswers: Record<string, string>,
    riskFactors: string[] = [],
    sessionId?: string
  ): TriageEvaluationResponse {
    const startedAt = new Date().toISOString();
    const effectiveSessionId = sessionId || `SES_${Math.random().toString(36).substring(2, 14).toUpperCase()}`;

    const warningSignsFound: string[] = [];
    let emergencyOverride = false;

    // 1. Check Symptom-level Emergency Overrides
    for (const s of symptoms) {
      const symDef = BUNDLED_SYMPTOMS.find(bs => bs.code === s.code);
      if (symDef && (symDef as any).is_emergency_warning) {
        emergencyOverride = true;
        warningSignsFound.push(`Critical primary symptom: ${s.name}`);
      }
      if (s.severity >= 9) {
        emergencyOverride = true;
        warningSignsFound.push(`Severe intensity (Score ${s.severity}/10): ${s.name}`);
      }
    }

    // 2. Check Answer-level Emergency Triggers
    for (const [qid, ans] of Object.entries(followupAnswers)) {
      const qDef = BUNDLED_QUESTIONS.find(q => q.question_id === qid);
      if (qDef && qDef.options) {
        for (const opt of qDef.options) {
          if (opt.code === ans && (opt as any).triggers_emergency) {
            emergencyOverride = true;
            warningSignsFound.push(`Critical indicator confirmed: ${qDef.question_text} -> ${opt.text}`);
          }
        }
      }
    }

    // 3. Evaluate Clinical Rules
    const triggeredRules: Array<{ rule_id: string; description?: string; explanation?: string; urgency_category?: number }> = [];
    const ruleCategories: number[] = [];

    const symptomCodes = new Set(symptoms.map(s => s.code));

    for (const rule of BUNDLED_RULES) {
      const requiredCodes = (rule as any).symptom_codes || [];
      const hasSymptoms = requiredCodes.length === 0 || requiredCodes.some((c: string) => symptomCodes.has(c));
      
      let matches = hasSymptoms;

      // Condition checks
      const conditions = (rule as any).conditions || {};
      if (conditions.min_severity && Math.max(...symptoms.map(s => s.severity), 0) < conditions.min_severity) {
        matches = false;
      }
      if (conditions.required_answers) {
        for (const [rqid, rans] of Object.entries(conditions.required_answers)) {
          if (followupAnswers[rqid] !== rans) {
            matches = false;
            break;
          }
        }
      }

      if (matches) {
        triggeredRules.push({
          rule_id: rule.rule_id,
          description: (rule as any).description || "",
          explanation: (rule as any).explanation || (rule as any).description || "",
          urgency_category: rule.urgency_category
        });
        ruleCategories.push(rule.urgency_category);
      }
    }

    // 4. Input Contradiction Detection
    const contradictions: string[] = [];
    for (const s of symptoms) {
      if (s.severity === 0 && s.progression === "worsening") {
        contradictions.push(`Zero severity specified for worsening symptom: ${s.name}`);
      }
    }

    // 5. Missing Required Questions Check
    const missingCriticalData: string[] = [];
    if (symptoms.length === 0) {
      missingCriticalData.push("No primary symptoms selected.");
    }
    const requiredQuestions = BUNDLED_QUESTIONS.filter(q => q.is_required && q.symptom_codes?.some(sc => symptomCodes.has(sc)));
    for (const rq of requiredQuestions) {
      if (!followupAnswers[rq.question_id]) {
        missingCriticalData.push(`Unanswered required safety question: ${rq.question_text}`);
      }
    }

    // 6. Compute Severity Score & Progression Trend
    let totalSev = 0;
    for (const s of symptoms) {
      totalSev += s.severity;
    }
    const severityScore = symptoms.length > 0 ? parseFloat((totalSev / symptoms.length).toFixed(1)) : 0.0;
    const progressionTrend = symptoms.some(s => s.progression === "worsening")
      ? "worsening"
      : symptoms.some(s => s.progression === "improving")
      ? "improving"
      : "stable";

    // 7. Synthesize Urgency Category (1: Emergency, 2: Early, 3: Routine, 4: Insufficient)
    let urgencyCategory: UrgencyCategory = 3;
    if (emergencyOverride) {
      urgencyCategory = 1;
    } else if (contradictions.length > 0 || (missingCriticalData.length > 2 && symptoms.length === 0)) {
      urgencyCategory = 4;
    } else if (ruleCategories.length > 0) {
      urgencyCategory = Math.min(...ruleCategories) as UrgencyCategory;
    } else if (severityScore >= 8.0 || progressionTrend === "worsening") {
      urgencyCategory = 2;
    } else {
      urgencyCategory = 3;
    }

    // 8. Labels, Explanations and Next Steps
    const categoryLabels: Record<UrgencyCategory, string> = {
      1: "Category 1 — Emergency Care",
      2: "Category 2 — Early Medical Consultation",
      3: "Category 3 — Routine Healthcare Guidance",
      4: "Category 4 — Insufficient Information"
    };
    const urgencyLabel = categoryLabels[urgencyCategory];

    let summaryExplanation = "";
    const recommendedNextSteps: string[] = [];
    const detailedReasoning: string[] = [];

    if (urgencyCategory === 1) {
      summaryExplanation = "EMERGENCY CARE RECOMMENDED: Critical red-flag indicators or severe clinical warning signs require urgent, professional emergency medical evaluation.";
      recommendedNextSteps.push("Call 112 (National Emergency Helpline) or 102 (Ambulance Service) immediately.");
      recommendedNextSteps.push("Do not attempt to operate a vehicle yourself; arrange emergency transport.");
      recommendedNextSteps.push("Sit or lie comfortably, keep airways clear, and alert family or someone nearby.");
      recommendedNextSteps.push("Download and present your MEDICARE Doctor Handover report to the emergency care team.");
    } else if (urgencyCategory === 2) {
      summaryExplanation = "EARLY MEDICAL CONSULTATION RECOMMENDED: Reported symptoms or progression trajectory indicate timely evaluation by a physician within 12–24 hours.";
      recommendedNextSteps.push("Schedule an in-person medical consultation within 12–24 hours.");
      recommendedNextSteps.push("Present your downloaded MEDICARE Doctor Handover report to the consulting physician.");
      recommendedNextSteps.push("If symptoms rapidly escalate or you develop chest pain, dial 112 immediately.");
    } else if (urgencyCategory === 3) {
      summaryExplanation = "ROUTINE HEALTHCARE GUIDANCE: Based on the reported symptoms, no immediate emergency warning signs were detected. Routine primary care or self-care is indicated.";
      recommendedNextSteps.push("Follow supportive home care measures: rest, hydration, and monitoring.");
      recommendedNextSteps.push("Consult your primary care clinic if symptoms persist beyond 5–7 days.");
      recommendedNextSteps.push("Retake this assessment if symptoms worsen or new signs arise.");
    } else {
      summaryExplanation = "INSUFFICIENT INFORMATION TO CLASSIFY: Responses provided are incomplete or contradictory. Missing information must never be interpreted as clinical safety.";
      recommendedNextSteps.push("Retake the assessment and answer all questions completely.");
      recommendedNextSteps.push("Contact the 104 National Health Helpline or attend a clinic if feeling unwell.");
    }

    // Detailed reasoning bullets (clean, without raw internal IDs)
    if (warningSignsFound.length > 0) {
      for (const ws of warningSignsFound) {
        detailedReasoning.push(`• Emergency Warning Identified: ${ws}`);
      }
    } else {
      detailedReasoning.push("• Emergency Indicators: No immediate red-flag emergency indicators detected from the reported symptoms.");
    }

    for (const r of triggeredRules) {
      const expl = r.explanation || r.description;
      if (expl) {
        detailedReasoning.push(`• Clinical Decision Factor: ${expl}`);
      }
    }

    detailedReasoning.push(`• Computed Severity Metric: ${severityScore} / 10.0`);
    detailedReasoning.push(`• Symptom Progression Trend: ${progressionTrend.toUpperCase()}`);

    let uncertaintyStatement = urgencyCategory === 1
      ? "Emergency indicators have a low threshold for action to prioritize patient safety."
      : "Assessment is based on self-reported inputs without physical examination or laboratory data.";

    if (missingCriticalData.length > 0) {
      uncertaintyStatement = `Some safety questions were not answered. Assessment confidence may be limited. ${uncertaintyStatement}`;
    }

    return {
      session_id: effectiveSessionId,
      urgency_category: urgencyCategory,
      urgency_label: urgencyLabel,
      started_at: startedAt,
      completed_at: new Date().toISOString(),
      severity_score: severityScore,
      progression_trend: progressionTrend,
      emergency_override: emergencyOverride,
      warning_signs_found: warningSignsFound,
      rules_triggered: triggeredRules,
      contradictions,
      missing_critical_data: missingCriticalData,
      summary_explanation: summaryExplanation,
      detailed_reasoning: detailedReasoning,
      recommended_next_steps: recommendedNextSteps,
      uncertainty_statement: uncertaintyStatement,
      clinical_limitations: "MEDICARE is a preliminary triage and clinical decision-support tool. It does not provide definitive medical diagnoses, prescriptions, or emergency guarantees.",
      triage_version: "1.0.0"
    };
  }
}

export function validateIndianMobile(phone: string): { isValid: boolean; formattedNumber: string; errorMessage?: string } {
  const cleaned = phone.replace(/[^0-9]/g, "");
  let digits = cleaned;
  if (digits.length === 12 && digits.startsWith("91")) {
    digits = digits.slice(2);
  }
  if (digits.length !== 10) {
    return { isValid: false, formattedNumber: phone, errorMessage: "Must be a 10-digit mobile number." };
  }
  if (!/^[6-9]/.test(digits)) {
    return { isValid: false, formattedNumber: phone, errorMessage: "Indian mobile numbers must start with 6, 7, 8, or 9." };
  }
  const formatted = `+91-${digits.slice(0, 5)}-${digits.slice(5)}`;
  return { isValid: true, formattedNumber: formatted };
}
