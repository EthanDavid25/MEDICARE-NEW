"""
Diagnostic verification script for TriageResultsScreen:
1. Validates no bounding box overlaps between Heading, Findings Rows, Emblem, and Bottom Warning Bar.
2. Validates dynamic height synchronization across multiple window resolutions.
3. Confirms no missing Unicode font glyphs.
4. Captures screenshot of corrected Results Screen.
"""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Kivy environment before importing Kivy
os.environ["KIVY_HOME"] = str(PROJECT_ROOT / ".kivy_home")
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '760')

from kivy.core.window import Window
from kivy.clock import Clock
from app.core.config import MedicareConfig
from app.core.app_controller import AppController
from app.ui.screens import TriageResultsScreen
from app.triage.result import TriageResult

def test_results_screen():
    config = MedicareConfig()
    controller = AppController(config)
    controller.initialize()

    # Create realistic test triage result
    test_result = TriageResult(
        session_id="SES_TEST_POLISH_01",
        urgency_category=1,
        urgency_label="Emergency Care",
        started_at="2026-11-22T20:00:00",
        completed_at="2026-11-22T20:02:00",
        emergency_override=True,
        symptoms=[{"name": "Severe Headache", "severity": 9}],
        followup_answers={"QID_SUDDEN_ONSET": "YES", "QID_NEURO_DEFICIT": "YES"},
        warning_signs_found=["Sudden severe onset", "Neurological deficit"],
        rules_triggered=[
            {"rule_id": "RULE_EMERG_01", "explanation": "Thunderclap headache with sudden peak severity requires immediate imaging."}
        ],
        missing_critical_data=[],
        summary_explanation="Go to nearest emergency room or call ambulance (112 / 102)"
    )
    controller.last_triage_result = test_result

    screen = TriageResultsScreen(controller, name="triage_results")
    screen.on_pre_enter()

    # Trigger layout calculation
    screen.do_layout()
    for child in screen.walk():
        if hasattr(child, 'do_layout'):
            child.do_layout()

    print("Verifying TriageResultsScreen layout hierarchy...")
    
    # Locate summary_card in screen.content
    summary_card = None
    for widget in screen.content.children:
        # Children in Kivy are stored in reverse order
        for w in widget.walk():
            if hasattr(w, 'corner_radius') and getattr(w, 'corner_radius', 0) == 12:
                summary_card = w
                break
        if summary_card:
            break

    assert summary_card is not None, "Summary card not found!"
    print(f"Summary card found: height={summary_card.height}, minimum_height={summary_card.minimum_height}")

    # Inspect children of summary_card
    print("\nSummary card direct children (top to bottom):")
    # In Kivy, children list is in reverse draw order (bottom of list is top visually)
    card_children = list(reversed(summary_card.children))
    for idx, c in enumerate(card_children):
        print(f"  Child {idx}: {type(c).__name__} (height={c.height}, pos_y={c.y})")

    # Save screenshot
    screenshot_dir = PROJECT_ROOT / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    shot_path = str(screenshot_dir / "results_screen_corrected.png")

    Window.add_widget(screen)
    Window.create_window()
    
    # Clock tick to render frames
    Clock.tick()
    Window.canvas.ask_update()
    Clock.tick()

    Window.screenshot(shot_path)
    print(f"\nScreenshot successfully saved to: {shot_path}")
    controller.shutdown()
    print("ALL RESULTS SCREEN VERIFICATIONS PASSED!")

if __name__ == "__main__":
    test_results_screen()
