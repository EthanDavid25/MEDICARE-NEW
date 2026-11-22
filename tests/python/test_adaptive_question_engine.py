"""
Comprehensive Automated Test Suite for MEDICARE Adaptive Question Engine.
Verifies all 10 clinical assessment scenarios, strict 7-word question constraint,
symptom-specific branching, answer-dependent follow-ups, safety overrides,
and deterministic question paths.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Sandboxed data home redirect
_TEST_DATA_HOME = tempfile.mkdtemp(prefix="medicare_adaptive_test_")
os.environ.setdefault("MEDICARE_DATA_HOME", _TEST_DATA_HOME)

local_kivy_home = PROJECT_ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from app.core.config import MedicareConfig
from app.core.database import SQLiteDatabase
from app.datasets.dataset_loader import DatasetLoader
from app.triage.engine import TriageEngine
from app.triage.question_engine import AdaptiveQuestionEngine, AdaptiveAssessmentSession


class TestAdaptiveQuestionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        cls.config = MedicareConfig(
            app_root=PROJECT_ROOT,
            db_path=cls.temp_path / "test.db",
            log_path=cls.temp_path / "test.log",
            data_dir=PROJECT_ROOT / "data",
            reports_dir=cls.temp_path / "reports",
            downloads_dir=cls.temp_path / "downloads"
        )
        cls.config.ensure_directories()
        cls.db = SQLiteDatabase(cls.config.db_path)
        cls.db.initialize()
        cls.patient_id = cls.db.execute(
            "INSERT INTO patients (display_name, created_at, updated_at) VALUES ('Test Patient', datetime('now'), datetime('now'))"
        ).lastrowid
        cls.loader = DatasetLoader(cls.config.data_dir, cls.db)
        cls.triage = TriageEngine(cls.loader, db=cls.db)
        cls.engine = cls.loader.get_question_engine()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db.close()
        except Exception:
            pass
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # CONSTRAINT 1: STRICT <= 7 WORDS ACROSS ALL QUESTIONS
    # -------------------------------------------------------------------------
    def test_01_all_questions_max_seven_words(self):
        """Verify that every single question in the dataset contains <= 7 words."""
        questions = self.loader.get_followup_questions()
        self.assertGreater(len(questions), 20, "Should have loaded full question set")

        for q in questions:
            qid = q.get("question_id")
            text = q.get("question_text", "")
            words = text.split()
            word_count = len(words)
            self.assertLessEqual(
                word_count,
                7,
                f"Question {qid} exceeded 7 words ({word_count} words): '{text}'"
            )
            self.assertGreaterEqual(
                word_count,
                3,
                f"Question {qid} is too short ({word_count} words): '{text}'"
            )

    # -------------------------------------------------------------------------
    # SCENARIO 1: IMPROVING MILD SYMPTOMS (Example A)
    # -------------------------------------------------------------------------
    def test_02_improving_mild_symptoms_few_questions_safety_preserved(self):
        """
        Example A: Mild symptoms (severity 2), improving.
        Expected: Fewer questions asked (<= 2), essential safety red-flag verified.
        """
        # Mild chest pain, improving
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_CHEST_PAIN", "name": "Chest Pain"}],
            severity=2,
            progression="improving",
            duration_days=1
        )
        # 1. Essential safety check is NEVER skipped
        q1 = session.get_next_question()
        self.assertIsNotNone(q1)
        self.assertEqual(q1["question_id"], "QID_CHEST_RADIATION")
        self.assertTrue(q1.get("is_emergency_safety_check"))
        session.record_answer(q1["question_id"], "NO")

        # 2. Confirms improvement
        q2 = session.get_next_question()
        self.assertIsNotNone(q2)
        self.assertEqual(q2["question_id"], "QID_CHEST_IMPROVING_CONFIRM")
        session.record_answer(q2["question_id"], "CONSISTENT_RESOLVING")

        # 3. Assessment terminates appropriately (does not subject to 10 questions)
        q3 = session.get_next_question()
        self.assertIsNone(q3, "Improving mild session should conclude after <= 2 targeted questions")
        self.assertLessEqual(len(session.asked_order), 2)

        # 4. Triage evaluation produces routine care
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[{"code": "SYM_CHEST_PAIN", "severity": 2, "progression": "improving"}],
            followup_answers=session.get_effective_answers()
        )
        self.assertEqual(result.urgency_category, 3, "Mild improving chest pain without radiation is Routine Care")

    # -------------------------------------------------------------------------
    # SCENARIO 2: WORSENING MODERATE SYMPTOMS (Example B)
    # -------------------------------------------------------------------------
    def test_03_worsening_moderate_symptoms_deeper_investigation(self):
        """
        Example B: Moderate symptoms (severity 6), getting worse.
        Expected: Deeper investigation into progression and resting pain (3-4 questions).
        """
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_CHEST_PAIN", "name": "Chest Pain"}],
            severity=6,
            progression="worsening",
            duration_days=2
        )
        # Question 1: Red flag check
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_CHEST_RADIATION")
        session.record_answer(q1["question_id"], "NO")

        # Question 2: Because worsening, investigates resting pain
        q2 = session.get_next_question()
        self.assertEqual(q2["question_id"], "QID_CHEST_WORSENING_RAPID")
        session.record_answer(q2["question_id"], "YES")

        # Question 3: Checks associated dyspnea / sweating
        q3 = session.get_next_question()
        self.assertEqual(q3["question_id"], "QID_CHEST_ASSOCIATED_DYSPNEA")
        session.record_answer(q3["question_id"], "NO")

        # Question depth reaches 3 questions for moderate worsening
        self.assertEqual(len(session.asked_order), 3)

    # -------------------------------------------------------------------------
    # SCENARIO 3: SEVERE SYMPTOMS & SAFETY OVERRIDES (Example C)
    # -------------------------------------------------------------------------
    def test_04_severe_symptoms_fast_path_safety_override(self):
        """
        Example C: Severe symptoms (severity 9) with emergency warning sign.
        Expected: Critical red flag prioritised, immediate escalation without long delay.
        """
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_CHEST_PAIN", "name": "Severe Chest Pain"}],
            severity=9,
            progression="worsening",
            duration_days=1
        )
        # Question 1: Red flag check
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_CHEST_RADIATION")
        # User answers YES (Emergency indicator!)
        session.record_answer(q1["question_id"], "YES")
        self.assertTrue(session.emergency_override_triggered)

        # Question 2: Rapid associated symptom check
        q2 = session.get_next_question()
        self.assertEqual(q2["question_id"], "QID_CHEST_ASSOCIATED_DYSPNEA")
        session.record_answer(q2["question_id"], "YES")

        # Question 3: Should STOP immediately to avoid delaying emergency care!
        q3 = session.get_next_question()
        self.assertIsNone(q3, "Critical emergency path must conclude promptly without delaying care")

        # Triage evaluation MUST override to Category 1
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[{"code": "SYM_CHEST_PAIN", "severity": 9, "progression": "worsening"}],
            followup_answers=session.get_effective_answers()
        )
        self.assertEqual(result.urgency_category, 1, "Must assign Category 1 (Emergency Care)")
        self.assertTrue(result.emergency_override)

    # -------------------------------------------------------------------------
    # SCENARIO 4: HEADACHE-SPECIFIC ASSESSMENT (Example D1)
    # -------------------------------------------------------------------------
    def test_05_headache_specific_branching(self):
        """Example D1: Headache presentation gets headache-specific questions."""
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_HEADACHE", "name": "Headache"}],
            severity=7,
            progression="worsening",
            duration_days=1
        )
        # Question 1: Thunderclap onset check
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_PAIN_ONSET_SUDDEN")
        session.record_answer(q1["question_id"], "NO")

        # Question 2: Because worsening, asks headache worsening signs (vision loss, vomiting)
        q2 = session.get_next_question()
        self.assertEqual(q2["question_id"], "QID_HEADACHE_WORSENING_SIGNS")
        session.record_answer(q2["question_id"], "NO")

        # Question 3: Vision changes
        q3 = session.get_next_question()
        self.assertEqual(q3["question_id"], "QID_HEADACHE_VISION")
        session.record_answer(q3["question_id"], "NO")

        # All questions must be headache/neuro relevant
        for qid in session.asked_order:
            self.assertTrue(
                any(k in qid for k in ["HEADACHE", "PAIN_ONSET", "VISION", "STROKE"]),
                f"Question {qid} is not relevant to headache!"
            )

    # -------------------------------------------------------------------------
    # SCENARIO 5: ABDOMINAL-SPECIFIC ASSESSMENT (Example D2)
    # -------------------------------------------------------------------------
    def test_06_abdominal_specific_branching(self):
        """Example D2: Abdominal presentation gets abdominal-specific questions."""
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_ABDOMINAL_PAIN", "name": "Abdominal Pain"}],
            severity=7,
            progression="worsening",
            duration_days=2
        )
        # Question 1: Board-like rigidity check (acute peritonitis)
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_ABD_RIGIDITY")
        session.record_answer(q1["question_id"], "NO")

        # Question 2: Bleeding signs check (GI hemorrhage)
        q2 = session.get_next_question()
        self.assertEqual(q2["question_id"], "QID_BLEEDING_SIGNS")
        session.record_answer(q2["question_id"], "NO")

        # Question 3: Pregnancy status check for abdominal pain
        q3 = session.get_next_question()
        self.assertEqual(q3["question_id"], "QID_PREGNANCY_STATUS")
        session.record_answer(q3["question_id"], "NOT_PREGNANT")

        # Must NOT ask unrelated questions like chest radiation or thunderclap
        self.assertNotIn("QID_CHEST_RADIATION", session.asked_order)
        self.assertNotIn("QID_RESP_SEVERITY", session.asked_order)

    # -------------------------------------------------------------------------
    # SCENARIO 6: BREATHING-SPECIFIC ASSESSMENT (Example D3)
    # -------------------------------------------------------------------------
    def test_07_breathing_specific_branching(self):
        """Example D3: Respiratory presentation gets respiratory-specific questions."""
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_SHORTNESS_OF_BREATH", "name": "Shortness of Breath"}],
            severity=8,
            progression="worsening",
            duration_days=1
        )
        # Question 1: Ability to speak full sentences
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_RESP_SEVERITY")
        session.record_answer(q1["question_id"], "SEVERE")

        # Question 2: Immediate stridor / airway compromise check
        q2 = session.get_next_question()
        self.assertEqual(q2["question_id"], "QID_RESP_STRIDOR_LIPS")
        session.record_answer(q2["question_id"], "YES")

        # Should escalate to emergency
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[{"code": "SYM_SHORTNESS_OF_BREATH", "severity": 8, "progression": "worsening"}],
            followup_answers=session.get_effective_answers()
        )
        self.assertEqual(result.urgency_category, 1, "Severe respiratory distress with stridor must be Category 1")

    # -------------------------------------------------------------------------
    # SCENARIO 7: DIFFERENT PAIN SEVERITY LEVELS INFLUENCE QUESTIONS
    # -------------------------------------------------------------------------
    def test_08_pain_severity_influences_question_selection(self):
        """Verify that pain severity (low vs high) changes question count and focus."""
        # Low severity unchanged headache (severity 2)
        sess_low = self.engine.create_session(
            symptoms=[{"code": "SYM_HEADACHE", "name": "Headache"}],
            severity=2,
            progression="unchanged",
            duration_days=1
        )
        q_low1 = sess_low.get_next_question()
        sess_low.record_answer(q_low1["question_id"], "NO")
        q_low2 = sess_low.get_next_question()
        self.assertEqual(q_low2["question_id"], "QID_HEADACHE_UNCHANGED_NATURE")
        sess_low.record_answer(q_low2["question_id"], "SIMILAR_NORMAL")
        self.assertIsNone(sess_low.get_next_question())  # Concludes early

        # High severity worsening headache (severity 9)
        sess_high = self.engine.create_session(
            symptoms=[{"code": "SYM_HEADACHE", "name": "Headache"}],
            severity=9,
            progression="worsening",
            duration_days=1
        )
        q_high1 = sess_high.get_next_question()
        self.assertEqual(q_high1["question_id"], "QID_PAIN_ONSET_SUDDEN")
        sess_high.record_answer(q_high1["question_id"], "YES")  # Thunderclap!
        self.assertTrue(sess_high.emergency_override_triggered)

    # -------------------------------------------------------------------------
    # SCENARIO 8: DIFFERENT SYMPTOM DURATIONS
    # -------------------------------------------------------------------------
    def test_09_duration_affects_fever_and_aliases(self):
        """Verify duration changes question selection (e.g. fever > 3 days) and aliases."""
        sess_short = self.engine.create_session(
            symptoms=[{"code": "SYM_FEVER", "name": "Fever"}],
            severity=4,
            progression="unchanged",
            duration_days=1
        )
        q1 = sess_short.get_next_question()
        self.assertEqual(q1["question_id"], "QID_FEVER_TEMP")
        sess_short.record_answer(q1["question_id"], "MODERATE")
        # Short fever does not immediately ask worsening days
        self.assertNotIn("QID_FEVER_WORSENING_DAYS", sess_short.asked_order)

        # Long fever (duration 4 days)
        sess_long = self.engine.create_session(
            symptoms=[{"code": "SYM_FEVER", "name": "Fever"}],
            severity=4,
            progression="unchanged",
            duration_days=4
        )
        q1 = sess_long.get_next_question()
        sess_long.record_answer(q1["question_id"], "MODERATE")
        q2 = sess_long.get_next_question()
        # Because duration >= 3 days, asks about fever days
        self.assertEqual(q2["question_id"], "QID_FEVER_WORSENING_DAYS")

    # -------------------------------------------------------------------------
    # SCENARIO 9: WARNING SIGNS & REASSURING ANSWERS OVERRIDDEN
    # -------------------------------------------------------------------------
    def test_10_warning_signs_override_reassuring_answers(self):
        """Verify that a positive red-flag cannot be overridden by reassuring answers."""
        session = self.engine.create_session(
            symptoms=[{"code": "SYM_ABDOMINAL_PAIN", "name": "Abdominal Pain"}],
            severity=7,
            progression="improving",  # User says improving...
            duration_days=1
        )
        # But board-like rigidity is confirmed (peritonitis)
        q1 = session.get_next_question()
        self.assertEqual(q1["question_id"], "QID_ABD_RIGIDITY")
        session.record_answer("QID_ABD_RIGIDITY", "YES")

        # Triage evaluation MUST be Category 1 regardless of "improving" claim
        result = self.triage.assess(
            patient_id=self.patient_id,
            symptoms=[{"code": "SYM_ABDOMINAL_PAIN", "severity": 7, "progression": "improving"}],
            followup_answers=session.get_effective_answers()
        )
        self.assertEqual(result.urgency_category, 1, "Board-like rigid abdomen must trigger Category 1 Emergency Care")
        self.assertTrue(result.emergency_override)

    # -------------------------------------------------------------------------
    # SCENARIO 10: DETERMINISTIC CONSISTENCY & NO REPEATED QUESTIONS
    # -------------------------------------------------------------------------
    def test_11_deterministic_and_no_repeated_questions(self):
        """Verify identical inputs yield identical sequences, and no question repeats."""
        def run_sim():
            sess = self.engine.create_session(
                symptoms=[{"code": "SYM_CHEST_PAIN", "name": "Chest Pain"}],
                severity=5,
                progression="unchanged",
                duration_days=2
            )
            q_order = []
            while True:
                q = sess.get_next_question()
                if not q:
                    break
                qid = q["question_id"]
                # Must not repeat
                self.assertNotIn(qid, q_order, f"Question {qid} was repeated!")
                q_order.append(qid)
                sess.record_answer(qid, "NO" if "NO" in [o["code"] for o in q.get("options", [])] else "POSITIONAL")
            return q_order

        run1 = run_sim()
        run2 = run_sim()
        self.assertEqual(run1, run2, "Identical inputs and answers must produce deterministic identical sequences")


if __name__ == "__main__":
    unittest.main()
