import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
os.environ["KIVY_HOME"] = str(ROOT / ".kivy_home")
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_LOG_LEVEL"] = "warning"

from app.core.config import load_config
from app.core.app_controller import AppController
from app.ui.app import MedicareKivyApp

def main():
    config = load_config()
    ctrl = AppController(config)
    ctrl.initialize()

    app = MedicareKivyApp(ctrl)
    root = app.build()

    # 1. Test Headache Assessment Flow
    print("Testing FollowupQuestionsScreen with Headache...")
    ctrl.assessment_staging = {
        "symptoms": [{"code": "SYM_HEADACHE", "name": "Headache", "severity": 6, "duration_value": 2, "duration_unit": "days", "progression": "worsening"}],
        "severity": 6,
        "duration_val": 2,
        "duration_unit": "days",
        "trajectory": "worsening"
    }

    fq_screen = app.screens["followup_questions"]
    fq_screen.on_pre_enter()
    print(f"Initial question history length: {len(fq_screen.history)}")
    assert len(fq_screen.history) >= 1

    # Check first question
    q0 = fq_screen.history[0]
    qid0 = q0.get("question_id")
    print(f"Q1 ID: {qid0} — Text: {q0.get('question_text')}")

    # Select an option on Q1
    opts = q0.get("options", [])
    val0 = opts[0].get("value", "YES") if opts else "YES"
    fq_screen._on_option_chosen(val0, None)
    assert fq_screen.session.answers.get(qid0) == val0
    print(f"Answer saved automatically: {qid0} = {val0}")

    # Advance to next question
    if len(fq_screen.history) > 1:
        fq_screen._advance_step(0)
        assert fq_screen.current_idx == 1
        q1 = fq_screen.history[1]
        print(f"Moved to Q2 ID: {q1.get('question_id')} — Text: {q1.get('question_text')}")

        # Press Back
        fq_screen._on_back_pressed()
        assert fq_screen.current_idx == 0
        assert fq_screen.session.answers.get(qid0) == val0
        print("Back button successfully restored Q1 and preserved previous answer!")

        # Move forward again
        fq_screen.current_idx = 1
        fq_screen._render_current_question()

    # Continue answering until complete
    max_steps = 10
    steps = 0
    while steps < max_steps:
        steps += 1
        curr_q = fq_screen.history[fq_screen.current_idx]
        c_opts = curr_q.get("options", [])
        c_val = c_opts[0].get("value", "NO") if c_opts else "NO"
        fq_screen._on_option_chosen(c_val, None)
        if fq_screen.current_idx < len(fq_screen.history) - 1:
            fq_screen._advance_step(0)
        else:
            break

    print(f"Total questions answered in session: {len(fq_screen.session.answers)}")
    assert len(fq_screen.session.answers) <= 4, f"Question limit exceeded: {len(fq_screen.session.answers)}"

    # Test submission
    fq_screen._evaluate_triage()
    assert ctrl.last_triage_result is not None
    print(f"Triage Result Category: {ctrl.last_triage_result.urgency_category} - {ctrl.last_triage_result.urgency_label}")

    # Test Triage Results Screen
    tr_screen = app.screens["triage_results"]
    tr_screen.on_pre_enter()
    print("TriageResultsScreen rendered successfully!")

    # Test Doctor Handover Screen with this result
    dh_screen = app.screens["doctor_handover"]
    dh_screen.on_pre_enter()
    print("DoctorHandoverScreen rendered successfully with live report preview!")

    ctrl.shutdown()
    print("\n>>> ALL ADAPTIVE CLINICAL FLOW & SCREEN TESTS PASSED! <<<")

if __name__ == "__main__":
    main()
