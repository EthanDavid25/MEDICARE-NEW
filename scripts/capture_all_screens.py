"""
Automated screen capture and visual verification script for MEDICARE.
Captures screenshots across all 12 screens at 1366x768 desktop resolution.
Window size MUST be set via kivy.config.Config BEFORE any kivy import to take effect.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

local_kivy_home = ROOT / ".kivy_home"
local_kivy_home.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(local_kivy_home)
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_LOG_LEVEL"] = "warning"

# Set window size via Config BEFORE any Kivy Window import — this is the only
# reliable way to enforce resolution on SDL2 (setting Window.size after import
# is ignored when SDL2 creates the display at native monitor resolution).
from kivy.config import Config
Config.set("graphics", "width", "1366")
Config.set("graphics", "height", "768")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "fullscreen", "0")

from kivy.core.window import Window

from app.core.config import load_config
from app.core.app_controller import AppController
from app.ui.app import MedicareKivyApp
from kivy.clock import Clock

class ScreenCaptureApp(MedicareKivyApp):
    def on_start(self):
        self.shot_dir = ROOT / "screenshots"
        self.shot_dir.mkdir(exist_ok=True)

        self.screen_sequence = [
            ("01_dashboard", "dashboard"),
            ("02_patient_profile", "patient_profile"),
            ("03_symptom_assessment", "symptom_assessment"),
            ("04_followup_questions", "followup_questions"),
            ("05_triage_results", "triage_results"),
            ("06_patient_history", "patient_history"),
            ("07_symptom_progression", "symptom_progression"),
            ("08_doctor_handover", "doctor_handover"),
            ("09_healthcare_directory", "healthcare_directory"),
            ("10_medical_references", "medical_references"),
            ("11_settings", "settings"),
            ("12_about", "about")
        ]
        self.current_idx = 0
        Clock.schedule_once(self.process_next_screen, 0.4)

    def process_next_screen(self, dt):
        if self.current_idx >= len(self.screen_sequence):
            print("\n>>> All 12 screens captured successfully. Stopping app. <<<")
            self.stop()
            return

        filename, s_id = self.screen_sequence[self.current_idx]
        self.navigate_to(s_id)
        scr = self.screens[s_id]
        scr.on_pre_enter()

        def do_shot(dt2):
            out_path = self.shot_dir / f"{filename}.png"
            Window.screenshot(name=str(out_path))
            print(f"[CAPTURED] Screen {self.current_idx+1}/12: '{s_id}' -> {out_path.name}")
            self.current_idx += 1
            Clock.schedule_once(self.process_next_screen, 0.3)

        Clock.schedule_once(do_shot, 0.3)

def run():
    config = load_config()
    controller = AppController(config)
    controller.initialize()

    # Pre-populate sample assessment and history so all screens render realistic data
    pid = controller.current_patient_id
    res = controller.triage_engine.assess(
        patient_id=pid,
        symptoms=[{
            "code": "SYM_CHEST_PAIN",
            "name": "Severe Chest Pain",
            "severity": 8,
            "duration_value": 2,
            "duration_unit": "days",
            "progression": "worsening"
        }],
        followup_answers={"QID_CHEST_RADIATION": "YES"}
    )
    controller.last_triage_result = res
    controller.assessment_staging = {
        "severity": 8,
        "progression": "worsening",
        "duration_days": 2,
        "symptoms": [{
            "code": "SYM_CHEST_PAIN",
            "name": "Severe Chest Pain",
            "severity": 8,
            "duration_value": 2,
            "duration_unit": "days",
            "progression": "worsening",
            "is_emergency_flag": True
        }]
    }

    app = ScreenCaptureApp(controller)
    app.run()
    controller.shutdown()

if __name__ == "__main__":
    run()
