"""MEDICARE application configuration management.

Supports both normal (source / folder-build) and PyInstaller onefile frozen modes.

Path strategy
─────────────
• Read-only bundled resources (data, assets, native libs):
    – Frozen onefile  → sys._MEIPASS  (temp extraction dir)
    – Dev / folder    → project root  (Path(__file__).parent.parent.parent)

• User-writable persistent data (DB, reports, logs, PDF downloads):
    – Always → %LOCALAPPDATA%\\MEDICARE  (never inside _MEIPASS, which is wiped on exit)
"""
from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import sys


def _get_resource_root() -> Path:
    """Return the root that contains bundled read-only resources.

    In a PyInstaller --onefile build ``sys._MEIPASS`` is the temp dir where
    the archive has been extracted.  In development or a folder-build it is
    the project root on disk.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


def _get_user_data_root() -> Path:
    """Return the per-user writable data directory for MEDICARE.

    Priority order:
    1. ``MEDICARE_DATA_HOME`` env var — allows tests / CI / sandbox to override.
    2. ``%LOCALAPPDATA%\\MEDICARE`` on Windows.
    3. ``~/Library/Application Support/MEDICARE`` on macOS.
    4. ``$XDG_DATA_HOME/MEDICARE`` or ``~/.local/share/MEDICARE`` on Linux.
    """
    # Test / CI / sandbox override
    override = os.environ.get("MEDICARE_DATA_HOME")
    if override:
        return Path(override)
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        return Path(localappdata) / "MEDICARE"
    # macOS
    home = Path.home()
    lib = home / "Library" / "Application Support"
    if lib.exists():
        return lib / "MEDICARE"
    # Linux / other
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "MEDICARE"
    return home / ".local" / "share" / "MEDICARE"


# Module-level singletons computed once at import time.
_RESOURCE_ROOT: Path = _get_resource_root()
_USER_DATA_ROOT: Path = _get_user_data_root()

# Keep APP_ROOT pointing at the resource root so that existing code that
# imports APP_ROOT directly continues to work for read-only paths.
APP_ROOT: Path = _RESOURCE_ROOT


@dataclass
class MedicareConfig:
    app_name: str = "MEDICARE"
    app_version: str = "1.0.0"

    # Read-only resource root (bundled files, datasets, native libs).
    app_root: Path = field(default_factory=lambda: _RESOURCE_ROOT)

    # ── User-writable paths (must survive onefile temp-dir deletion) ──────
    db_path: Path = field(
        default_factory=lambda: _USER_DATA_ROOT / "data" / "database" / "medicare.db"
    )
    log_path: Path = field(
        default_factory=lambda: _USER_DATA_ROOT / "logs" / "medicare.log"
    )

    # ── Read-only resource paths (bundled with the executable) ────────────
    data_dir: Path = field(default_factory=lambda: _RESOURCE_ROOT / "data")
    medical_data_dir: Path = field(
        default_factory=lambda: _RESOURCE_ROOT / "data" / "medical"
    )
    healthcare_data_dir: Path = field(
        default_factory=lambda: _RESOURCE_ROOT / "data" / "healthcare"
    )
    native_dir: Path = field(default_factory=lambda: _RESOURCE_ROOT / "native")

    # ── Additional user-writable directories ─────────────────────────────
    reports_dir: Path = field(
        default_factory=lambda: _USER_DATA_ROOT / "reports"
    )
    downloads_dir: Path = field(
        default_factory=lambda: _USER_DATA_ROOT / "downloads"
    )

    encryption_enabled: bool = False
    offline_mode: bool = True
    triage_version: str = "1.0.0"
    log_level: str = "INFO"

    def ensure_directories(self):
        """Create required directories if they do not exist."""
        for d in (
            self.db_path.parent,
            self.log_path.parent,
            self.reports_dir,
            self.downloads_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        return {k: str(v) if isinstance(v, Path) else v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "MedicareConfig":
        path_fields = {
            "app_root", "db_path", "log_path", "data_dir",
            "medical_data_dir", "healthcare_data_dir", "native_dir",
            "reports_dir", "downloads_dir",
        }
        kwargs = {}
        for k, v in data.items():
            if k in path_fields:
                kwargs[k] = Path(v)
            else:
                kwargs[k] = v
        return cls(**kwargs)


def load_config(config_file: Path = None) -> MedicareConfig:
    """Load config from JSON file or return defaults."""
    if config_file is None:
        # Config file lives beside the user DB (writable location).
        config_file = _USER_DATA_ROOT / "config.json"
        # Fallback: check the old resource-root location so existing
        # developer machines with a checked-in config.json still work.
        if not config_file.exists():
            legacy = _RESOURCE_ROOT / "config.json"
            if legacy.exists():
                config_file = legacy
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return MedicareConfig.from_dict(data)
        except Exception:
            pass
    return MedicareConfig()


def save_config(config: MedicareConfig, config_file: Path = None):
    """Save config to JSON file (always to the writable user-data location)."""
    if config_file is None:
        config_file = _USER_DATA_ROOT / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)

