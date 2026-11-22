"""
MEDICARE — Medical Symptoms Triage Advisor
Cross-Platform Application Entry Point (Android + Windows)
Runs locally and offline using Python, C, Kivy, and SQLite.
"""
import sys
import os
import logging
from pathlib import Path

# ── PyInstaller frozen-build: add _MEIPASS to sys.path so app.* imports work ──
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    meipass = Path(sys._MEIPASS)
    if str(meipass) not in sys.path:
        sys.path.insert(0, str(meipass))

# ── Ensure project root is on sys.path (dev / folder-build mode) ──────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Configure Kivy input before any subsystem loads ───────────────────────────
from kivy.config import Config as KivyConfig
KivyConfig.set("input", "mouse", "mouse,disable_multitouch")

from app.core.config import load_config
from app.core.app_controller import AppController


def _write_crash_log(exc: BaseException):
    """Write crash details to a file accessible to the user."""
    import traceback, tempfile, datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_path = Path(tempfile.gettempdir()) / f"MEDICARE_crash_{ts}.log"
    try:
        with open(crash_path, "w", encoding="utf-8") as f:
            f.write(f"MEDICARE Fatal Crash — {datetime.datetime.now()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
            f.write(f"MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}\n")
            f.write(f"sys.path: {sys.path}\n\n")
            traceback.print_exc(file=f)
        print(f"[MEDICARE] Crash log written to: {crash_path}", file=sys.stderr)
    except Exception:
        pass


def main():
    """Application startup sequence."""
    try:
        config = load_config()
        controller = AppController(config)
        controller.initialize()
        controller.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        _write_crash_log(e)
        logging.getLogger("medicare").critical(
            "Fatal error during execution: %s", e, exc_info=True
        )
    finally:
        try:
            if "controller" in dir() and controller:
                controller.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
