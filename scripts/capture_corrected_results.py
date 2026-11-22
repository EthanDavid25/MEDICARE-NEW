"""
Capture high-fidelity screenshot of the full MEDICARE application showing
the corrected Triage Results Screen.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["KIVY_HOME"] = str(ROOT / ".kivy_home")
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '760')
Config.set('graphics', 'resizable', '0')

from kivy.core.window import Window
from kivy.clock import Clock
from app.core.config import MedicareConfig
from app.core.app_controller import AppController
from app.ui.app import MedicareKivyApp
from app.triage.result import TriageResult

def capture():
    config = MedicareConfig()
    controller = AppController(config)
    controller.initialize()

    app = MedicareKivyApp(controller)
    root_widget = app.build()

    test_result = TriageResult(
        session_id="SES_AUDIT_20261122",
        urgency_category=1,
        urgency_label="Emergency Care",
        started_at="2026-11-22T20:00:00",
        completed_at="2026-11-22T20:02:00",
        emergency_override=True,
        symptoms=[{"name": "Severe Headache", "severity": 9}],
        followup_answers={"QID_SUDDEN_ONSET": "YES", "QID_NEURO_DEFICIT": "YES"},
        warning_signs_found=["Sudden severe onset", "Neurological deficit"],
        rules_triggered=[
            {"rule_id": "RULE_HEADACHE_EMERG", "explanation": "Sudden onset severe headache with neurological deficit."}
        ],
        missing_critical_data=[],
        summary_explanation="Go to nearest emergency room or call ambulance (112 / 102)"
    )
    controller.last_triage_result = test_result

    # Add root_widget to Window
    Window.add_widget(root_widget)
    app.navigate_to("triage_results")

    # Tick clock to process all layout & rendering events
    for _ in range(8):
        Clock.tick()
        Window.canvas.ask_update()

    shot_name = "corrected_results_screen.png"
    shot_path = str(ROOT / "screenshots" / shot_name)
    Window.screenshot(shot_path)
    print(f"Captured full-screen results to: {shot_path}")
    controller.shutdown()

if __name__ == "__main__":
    capture()
