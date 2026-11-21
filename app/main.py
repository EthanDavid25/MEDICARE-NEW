"""
MEDICARE — Medical Symptoms Triage Advisor
Cross-Platform Application Entry Point (Android + Windows)
Runs locally and offline using Python, C, Kivy, and SQLite.
"""
import sys
import logging
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import load_config
from app.core.app_controller import AppController

def main():
    """Application startup sequence."""
    config = load_config()
    controller = AppController(config)
    try:
        controller.initialize()
        controller.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.getLogger("medicare").critical("Fatal error encountered during execution: %s", e)
    finally:
        controller.shutdown()

if __name__ == "__main__":
    main()
