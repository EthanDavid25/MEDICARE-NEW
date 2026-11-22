"""
MEDICARE Crash Diagnostic Script.
Captures the actual startup exception that causes the black-window-then-close crash
when running the PyInstaller frozen executable.

Simulates the frozen executable environment as closely as possible:
- Uses LOCALAPPDATA for user data (no MEDICARE_DATA_HOME override)
- Clears any dev environment variables
- Tests full startup sequence through Kivy App.build()
- Logs all exceptions to both stdout and a crash log file
"""
import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# --- Clear dev-mode environment overrides to simulate frozen execution ---
os.environ.pop("MEDICARE_DATA_HOME", None)
os.environ.pop("KIVY_HOME", None)

# Use a local kivy home for the test to avoid permission issues
SCRIPT_DIR = Path(__file__).resolve().parent
KIVY_HOME_DIR = SCRIPT_DIR.parent / ".kivy_home_diag"
KIVY_HOME_DIR.mkdir(exist_ok=True)
os.environ["KIVY_HOME"] = str(KIVY_HOME_DIR)

# Log file for crash output
LOG_FILE = SCRIPT_DIR.parent / "data" / "crash_diagnostic.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_diagnostic():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== MEDICARE Crash Diagnostic: {datetime.now()} ===\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n\n")

    log("=== MEDICARE CRASH DIAGNOSTIC START ===")
    log(f"Python {sys.version}")
    log(f"ROOT: {ROOT}")

    # --- STEP 1: Config ---
    log("\n--- STEP 1: load_config() ---")
    try:
        from app.core.config import load_config, _get_user_data_root
        cfg = load_config()
        user_data = _get_user_data_root()
        log(f"  user_data_root:    {user_data}")
        log(f"  LOCALAPPDATA:      {os.environ.get('LOCALAPPDATA', 'NOT SET')}")
        log(f"  resource_root:     {cfg.app_root}")
        log(f"  db_path:           {cfg.db_path}")
        log(f"  medical_data_dir:  {cfg.medical_data_dir}")
        log(f"  medical_data_dir exists: {cfg.medical_data_dir.exists()}")
        log(f"  native_dir:        {cfg.native_dir}")
        log(f"  native_dir exists: {cfg.native_dir.exists()}")
        # Try creating directories (this hits LOCALAPPDATA which may cause PermissionError)
        try:
            cfg.ensure_directories()
            log("  ensure_directories() OK")
        except Exception as de:
            log(f"  FAIL ensure_directories(): {type(de).__name__}: {de}")
            traceback.print_exc()
    except Exception as e:
        log(f"  FAIL load_config: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    # --- STEP 2: Logger ---
    log("\n--- STEP 2: Logger init ---")
    try:
        import logging
        logger = logging.getLogger("medicare")
        log(f"  Logger: {logger}")
        log("  Logger OK")
    except Exception as e:
        log(f"  FAIL: {type(e).__name__}: {e}")

    # --- STEP 3: AppController ---
    log("\n--- STEP 3: AppController.initialize() ---")
    controller = None
    try:
        from app.core.app_controller import AppController
        controller = AppController(cfg)
        controller.initialize()
        log("  AppController.initialize() OK")
        log(f"  current_patient_id: {controller.current_patient_id}")
    except Exception as e:
        log(f"  FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    # --- STEP 4: Kivy App build() ---
    log("\n--- STEP 4: MedicareKivyApp.build() ---")
    try:
        from app.ui.app import MedicareKivyApp
        app = MedicareKivyApp(controller)
        root_widget = app.build()
        log(f"  build() returned: {root_widget}")
        log("  MedicareKivyApp.build() OK")
    except Exception as e:
        log(f"  FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        if controller:
            controller.shutdown()
        return

    # --- STEP 5: Screen pre_enter ---
    log("\n--- STEP 5: All screen on_pre_enter() ---")
    for name, screen in app.screens.items():
        try:
            screen.on_pre_enter()
            log(f"  {name}: OK")
        except Exception as e:
            log(f"  {name}: FAIL - {type(e).__name__}: {e}")
            traceback.print_exc()

    controller.shutdown()
    log(f"\n=== DIAGNOSTIC COMPLETE. Log saved to: {LOG_FILE} ===")


if __name__ == "__main__":
    run_diagnostic()
