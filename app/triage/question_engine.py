"""
MEDICARE Adaptive Question Engine.
Provides dynamic, answer-dependent question selection tailored to:
- Selected symptoms & body systems
- Pain severity (1-10)
- Symptom duration & trajectory (improving / unchanged / worsening)
- Associated symptoms & previous answers in current assessment
- Immediate safety overrides & emergency red flags

Rules:
- Every question text is strictly <= 7 words (3-6 preferred).
- Next question depends on answers already provided.
- Prevents repeated questions.
- Stops appropriately when sufficient clinical data is gathered or emergency is confirmed.
- Deterministic: identical inputs produce identical question paths.
"""
import logging
from typing import Optional, Any

logger = logging.getLogger("medicare.question_engine")


class AdaptiveQuestionEngine:
    """Context-dependent clinical question selection engine."""

    def __init__(self, dataset_loader):
        self.dataset_loader = dataset_loader
        self._questions_by_id: dict[str, dict] = {}
        self._load_questions()

    def _load_questions(self):
        questions = self.dataset_loader.get_followup_questions()
        for q in questions:
            qid = q.get("question_id")
            if qid:
                self._questions_by_id[qid] = q

    def get_question(self, qid: str) -> Optional[dict]:
        return self._questions_by_id.get(qid)

    def create_session(
        self,
        symptoms: list[dict],
        severity: int = 5,
        progression: str = "unchanged",
        duration_days: int = 1,
    ) -> "AdaptiveAssessmentSession":
        """Spawns a new stateful assessment session."""
        return AdaptiveAssessmentSession(
            engine=self,
            symptoms=symptoms,
            severity=severity,
            progression=progression,
            duration_days=duration_days,
        )


class AdaptiveAssessmentSession:
    """Stateful assessment session tracking dynamic question progression."""

    def __init__(
        self,
        engine: AdaptiveQuestionEngine,
        symptoms: list[dict],
        severity: int = 5,
        progression: str = "unchanged",
        duration_days: int = 1,
    ):
        self.engine = engine
        self.symptoms = symptoms or []
        self.severity = int(severity)
        self.progression = str(progression or "unchanged").lower()
        self.duration_days = int(duration_days)
        self.answers: dict[str, str] = {}
        self.asked_order: list[str] = []
        self.emergency_override_triggered = False

        # Identify primary symptom codes and categories
        self.symptom_codes = {s.get("code") for s in self.symptoms if s.get("code")}
        self.primary_systems = self._identify_body_systems()

        # Compute max question budget based on clinical tier:
        # Tier A (Mild & Improving): 1-2 questions (red flag check + resolution check)
        # Tier B (Mild/Moderate & Unchanged): 2-3 questions
        # Tier C (Moderate & Worsening): 3-4 questions (progression + associated + red flag)
        # Tier D (Severe >= 8): 2-3 high-priority emergency checks, fast-path to urgent care
        if self.severity <= 3 and self.progression == "improving":
            self.max_questions = 2
        elif self.severity >= 8:
            self.max_questions = 3
        elif self.progression == "worsening":
            self.max_questions = 4
        else:
            self.max_questions = 3

    def _identify_body_systems(self) -> set[str]:
        systems = set()
        for sym in self.engine.dataset_loader.get_symptoms():
            code = sym.get("code")
            if code in self.symptom_codes:
                bs = sym.get("body_system", "").lower()
                if bs:
                    systems.add(bs)
                cat = sym.get("category", "").lower()
                if cat:
                    systems.add(cat)
        # Also check common code prefixes
        for code in self.symptom_codes:
            c = code.upper()
            if "CHEST" in c or "HEART" in c or "PALPITATION" in c:
                systems.add("chest")
                systems.add("cardiovascular")
            if "HEADACHE" in c or "MIGRAINE" in c or "CONFUSION" in c or "STROKE" in c or "NUMB" in c:
                systems.add("headache")
                systems.add("neurological")
            if "BREATH" in c or "RESP" in c or "COUGH" in c or "WHEEZ" in c or "DYSPNEA" in c:
                systems.add("respiratory")
            if "ABDOM" in c or "BELLY" in c or "STOMACH" in c or "NAUSEA" in c or "VOMIT" in c or "DIARRHEA" in c:
                systems.add("abdominal")
                systems.add("digestive")
            if "FEVER" in c or "CHILL" in c:
                systems.add("fever")
            if "JOINT" in c or "BACK" in c or "NECK" in c or "LEG" in c or "FRACTURE" in c:
                systems.add("musculoskeletal")
            if "DIZZY" in c or "SYNCOPE" in c or "FAINT" in c:
                systems.add("dizziness")
        return systems

    def record_answer(self, question_id: str, answer_code: str):
        """Records an answer and evaluates immediate safety triggers."""
        self.answers[question_id] = answer_code
        if question_id not in self.asked_order:
            self.asked_order.append(question_id)

        # Check if this answer triggers an emergency safety flag
        q_def = self.engine.get_question(question_id)
        if q_def:
            for opt in q_def.get("options", []):
                if opt.get("code") == answer_code and opt.get("triggers_emergency", False):
                    self.emergency_override_triggered = True
                    logger.warning(
                        "Emergency trigger activated: Question %s -> %s",
                        question_id,
                        answer_code,
                    )

    def get_effective_answers(self) -> dict[str, str]:
        """Returns answers including automatic derived triage aliases."""
        eff = dict(self.answers)

        # Derived rule aliases for complete compatibility with triage rules:
        if "QID_RESP_STRIDOR_LIPS" in eff and "QID_RESP_STRIDOR" not in eff:
            eff["QID_RESP_STRIDOR"] = eff["QID_RESP_STRIDOR_LIPS"]

        if "QID_FEVER_IMMUNO_RISK" in eff and "QID_IMMUNOSUPPRESSED" not in eff:
            eff["QID_IMMUNOSUPPRESSED"] = eff["QID_FEVER_IMMUNO_RISK"]

        if "QID_DIZZINESS_SYNCOPE" in eff and "QID_SYNCOPE_EPISODE" not in eff:
            eff["QID_SYNCOPE_EPISODE"] = eff["QID_DIZZINESS_SYNCOPE"]

        # Progression alias
        if "QID_SYMPTOM_PROGRESSION" not in eff:
            if self.progression == "worsening":
                eff["QID_SYMPTOM_PROGRESSION"] = (
                    "WORSENING_RAPIDLY" if self.severity >= 8 else "WORSENING_SLOWLY"
                )
            elif self.progression == "improving":
                eff["QID_SYMPTOM_PROGRESSION"] = "IMPROVING"
            else:
                eff["QID_SYMPTOM_PROGRESSION"] = "UNCHANGED"

        # Duration alias
        if "QID_SYMPTOM_DURATION" not in eff:
            if self.duration_days >= 14:
                eff["QID_SYMPTOM_DURATION"] = "WEEKS"
            elif self.duration_days >= 2:
                eff["QID_SYMPTOM_DURATION"] = "DAYS"
            else:
                eff["QID_SYMPTOM_DURATION"] = "HOURS"

        return eff

    def get_next_question(self) -> Optional[dict]:
        """
        Dynamically selects the next question based on current state,
        answers provided so far, symptom profile, severity, and trajectory.
        Returns None when assessment is complete.
        """
        # If max question budget reached, stop
        if len(self.asked_order) >= self.max_questions:
            return None

        # If emergency was triggered and we already asked associated checks (up to 2 checks), stop
        if self.emergency_override_triggered and len(self.asked_order) >= 3:
            return None

        asked = set(self.asked_order)

        # Helper to pick candidate if not asked
        def candidate(qid: str) -> Optional[dict]:
            if qid not in asked:
                q = self.engine.get_question(qid)
                if q:
                    return q
            return None

        # -------------------------------------------------------------
        # BRANCH 1: CHEST / CARDIOVASCULAR
        # -------------------------------------------------------------
        if "chest" in self.primary_systems or "cardiovascular" in self.primary_systems:
            # 1. Primary Red Flag Check: Chest pain radiation
            q = candidate("QID_CHEST_RADIATION")
            if q:
                return q

            # User answered QID_CHEST_RADIATION
            rad_ans = self.answers.get("QID_CHEST_RADIATION")
            if rad_ans == "YES":
                # Emergency confirmed: next ask associated breathlessness / sweating
                q = candidate("QID_CHEST_ASSOCIATED_DYSPNEA")
                if q:
                    return q
                return None  # Stop to avoid delaying emergency care

            # If radiation was NO:
            if self.progression == "improving" and self.severity <= 4:
                # Improving path: check if improvement is consistent
                q = candidate("QID_CHEST_IMPROVING_CONFIRM")
                if q:
                    return q
            elif self.progression == "worsening":
                # Worsening path: check rest pain
                q = candidate("QID_CHEST_WORSENING_RAPID")
                if q:
                    return q
                # If resting pain answered, check associated dyspnea
                q = candidate("QID_CHEST_ASSOCIATED_DYSPNEA")
                if q:
                    return q
            else:
                # Unchanged: check duration & associated signs
                q = candidate("QID_CHEST_UNCHANGED_DURATION")
                if q:
                    return q
                if self.severity >= 6:
                    q = candidate("QID_CHEST_ASSOCIATED_DYSPNEA")
                    if q:
                        return q

        # -------------------------------------------------------------
        # BRANCH 2: HEADACHE / NEUROLOGICAL
        # -------------------------------------------------------------
        if "headache" in self.primary_systems or "neurological" in self.primary_systems:
            # Check for stroke/FAST signs if confusion, numbness, or limb weakness
            if any(k in self.symptom_codes for k in ["SYM_CONFUSION", "SYM_NUMBNESS", "SYM_WEAKNESS_LIMB"]):
                q = candidate("QID_STROKE_FAST_FACE")
                if q:
                    return q
                if self.answers.get("QID_STROKE_FAST_FACE") == "YES":
                    return None  # Emergency stroke flag!
                q = candidate("QID_STROKE_FAST_ARM")
                if q:
                    return q
                if self.answers.get("QID_STROKE_FAST_ARM") == "YES":
                    return None
                q = candidate("QID_STROKE_FAST_SPEECH")
                if q:
                    return q
                if self.answers.get("QID_STROKE_FAST_SPEECH") == "YES":
                    return None

            # Primary Red Flag: Sudden thunderclap onset
            q = candidate("QID_PAIN_ONSET_SUDDEN")
            if q:
                return q

            sudden_ans = self.answers.get("QID_PAIN_ONSET_SUDDEN")
            if sudden_ans == "YES":
                # Thunderclap confirmed: check worsening confusion / vision loss
                q = candidate("QID_HEADACHE_WORSENING_SIGNS")
                if q:
                    return q
                return None

            # If fever is present alongside headache, check stiff neck (meningismus)
            if "fever" in self.primary_systems or "SYM_FEVER" in self.symptom_codes:
                q = candidate("QID_HEADACHE_STIFF_NECK")
                if q:
                    return q
                if self.answers.get("QID_HEADACHE_STIFF_NECK") == "NO":
                    return None  # Stiff neck confirmed emergency

            # Trajectory follow-ups
            if self.progression == "improving" and self.severity <= 3:
                q = candidate("QID_GENERAL_IMPROVEMENT_NEW_SIGNS")
                if q:
                    return q
            elif self.progression == "worsening":
                q = candidate("QID_HEADACHE_WORSENING_SIGNS")
                if q:
                    return q
                q = candidate("QID_HEADACHE_VISION")
                if q:
                    return q
            else:
                # Unchanged
                q = candidate("QID_HEADACHE_UNCHANGED_NATURE")
                if q:
                    return q
                if self.severity >= 6:
                    q = candidate("QID_HEADACHE_VISION")
                    if q:
                        return q

        # -------------------------------------------------------------
        # BRANCH 3: RESPIRATORY / BREATHING
        # -------------------------------------------------------------
        if "respiratory" in self.primary_systems:
            # 1. Check ability to speak full sentences
            q = candidate("QID_RESP_SEVERITY")
            if q:
                return q

            if self.answers.get("QID_RESP_SEVERITY") == "SEVERE":
                # Critical respiratory distress: check stridor / lip swelling immediately
                q = candidate("QID_RESP_STRIDOR_LIPS")
                if q:
                    return q
                return None

            # 2. Check stridor / lip swelling
            q = candidate("QID_RESP_STRIDOR_LIPS")
            if q:
                return q
            if self.answers.get("QID_RESP_STRIDOR_LIPS") == "YES":
                return None  # Airway emergency

            # 3. Speed of worsening
            if self.progression == "worsening":
                q = candidate("QID_RESP_WORSENING_SPEED")
                if q:
                    return q
            elif self.progression == "improving":
                q = candidate("QID_GENERAL_IMPROVEMENT_NEW_SIGNS")
                if q:
                    return q

        # -------------------------------------------------------------
        # BRANCH 4: ABDOMINAL / DIGESTIVE
        # -------------------------------------------------------------
        if "abdominal" in self.primary_systems or "digestive" in self.primary_systems:
            # 1. Primary Red Flag: Rigid abdomen (peritonitis)
            q = candidate("QID_ABD_RIGIDITY")
            if q:
                return q
            if self.answers.get("QID_ABD_RIGIDITY") == "YES":
                q = candidate("QID_BLEEDING_SIGNS")
                if q:
                    return q
                return None

            # 2. Bleeding signs (vomiting blood / black stool)
            q = candidate("QID_BLEEDING_SIGNS")
            if q:
                return q
            if self.answers.get("QID_BLEEDING_SIGNS") == "YES":
                return None

            # 3. Pregnancy check for abdominal pain
            if "SYM_ABDOMINAL_PAIN" in self.symptom_codes and self.severity >= 5:
                q = candidate("QID_PREGNANCY_STATUS")
                if q:
                    return q

            # 4. Dehydration check
            if any(k in self.symptom_codes for k in ["SYM_NAUSEA_VOMITING", "SYM_DIARRHEA"]):
                q = candidate("QID_DIGEST_DEHYDRATION")
                if q:
                    return q

            if self.progression == "improving":
                q = candidate("QID_GENERAL_IMPROVEMENT_NEW_SIGNS")
                if q:
                    return q

        # -------------------------------------------------------------
        # BRANCH 5: FEVER / INFECTION
        # -------------------------------------------------------------
        if "fever" in self.primary_systems:
            # 1. Highest fever temp
            q = candidate("QID_FEVER_TEMP")
            if q:
                return q

            temp_ans = self.answers.get("QID_FEVER_TEMP")
            if temp_ans == "HIGH_GRADE":
                # High grade: check immunosuppression immediately
                q = candidate("QID_FEVER_IMMUNO_RISK")
                if q:
                    return q

            # If worsening or duration >= 3 days
            if self.progression == "worsening" or self.duration_days >= 3:
                q = candidate("QID_FEVER_WORSENING_DAYS")
                if q:
                    return q

            # Check immunosuppression if not yet asked
            if self.severity >= 6:
                q = candidate("QID_FEVER_IMMUNO_RISK")
                if q:
                    return q

            if self.progression == "improving":
                q = candidate("QID_GENERAL_IMPROVEMENT_NEW_SIGNS")
                if q:
                    return q

        # -------------------------------------------------------------
        # BRANCH 6: DIZZINESS / SYNCOPE
        # -------------------------------------------------------------
        if "dizziness" in self.primary_systems:
            q = candidate("QID_DIZZINESS_SYNCOPE")
            if q:
                return q
            if self.answers.get("QID_DIZZINESS_SYNCOPE") == "YES":
                # Syncope: check FAST face
                q = candidate("QID_STROKE_FAST_FACE")
                if q:
                    return q
                return None

        # -------------------------------------------------------------
        # BRANCH 7: MUSCULOSKELETAL / TRAUMA
        # -------------------------------------------------------------
        if "musculoskeletal" in self.primary_systems:
            q = candidate("QID_MSK_DEFORMITY_WEIGHT")
            if q:
                return q
            if any(k in self.symptom_codes for k in ["SYM_LEG_PAIN", "SYM_SWELLING"]):
                q = candidate("QID_CALF_SWELLING")
                if q:
                    return q

        # -------------------------------------------------------------
        # FALLBACK GENERAL QUESTIONS
        # -------------------------------------------------------------
        if self.progression == "improving":
            q = candidate("QID_GENERAL_IMPROVEMENT_NEW_SIGNS")
            if q:
                return q

        if self.severity >= 7:
            q = candidate("QID_PAIN_ONSET_SUDDEN")
            if q:
                return q

        # No more relevant questions for this clinical context
        return None
