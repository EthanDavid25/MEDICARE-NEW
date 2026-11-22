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


def _is_writable(path: Path) -> bool:
    """Safely check if *path* can be created and written to."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / f".write_test_{os.getpid()}.tmp"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return True
    except Exception:
        return False


def _get_user_data_root() -> Path:
    """Return the per-user writable data directory for MEDICARE.

    Priority order:
    1. ``MEDICARE_DATA_HOME`` env var — allows tests / CI / sandbox to override.
    2. Writable ``MEDICARE_Data`` folder beside the executable (portable mode).
    3. ``%LOCALAPPDATA%\\MEDICARE`` on Windows.
    4. ``%APPDATA%\\MEDICARE`` on Windows.
    5. ``Documents\\MEDICARE`` on Windows.
    6. System temp directory (``%TEMP%\\MEDICARE``) — guaranteed writable.
    """
    import tempfile

    # 1. Test / CI / sandbox override
    override = os.environ.get("MEDICARE_DATA_HOME")
    if override and _is_writable(Path(override)):
        return Path(override)

    candidates: list[Path] = []

    # 2. Portable mode: beside the executable if writable
    if getattr(sys, "frozen", False):
        try:
            exe_dir = Path(sys.executable).parent
            candidates.append(exe_dir / "MEDICARE_Data")
        except Exception:
            pass

    # 3. Platform-specific user data paths
    if sys.platform == "win32":
        for env_var in ("LOCALAPPDATA", "APPDATA"):
            root = os.environ.get(env_var)
            if root:
                candidates.append(Path(root) / "MEDICARE")
        try:
            candidates.append(Path.home() / "Documents" / "MEDICARE")
        except Exception:
            pass
    elif sys.platform == "darwin":
        candidates.append(Path.home() / "Library" / "Application Support" / "MEDICARE")
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            candidates.append(Path(xdg) / "MEDICARE")
        candidates.append(Path.home() / ".local" / "share" / "MEDICARE")

    # 4. Fallback: temp directory (guaranteed writable on all platforms)
    candidates.append(Path(tempfile.gettempdir()) / "MEDICARE")

    for candidate in candidates:
        if _is_writable(candidate):
            return candidate

    return Path(tempfile.gettempdir()) / "MEDICARE"


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
        """Create required directories if they do not exist.

        Wrapped in individual try/except so a PermissionError on one writable path
        (e.g. OneDrive-redirected LOCALAPPDATA on Windows) does not block the others.
        """
        for d in (
            self.db_path.parent,
            self.log_path.parent,
            self.reports_dir,
            self.downloads_dir,
        ):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError):
                # Non-fatal: the directory may already exist or be accessible via
                # a different code path.  Log to stderr only (logger not yet set up).
                import sys as _sys
                print(f"[MEDICARE] WARNING: Could not create directory: {d}", file=_sys.stderr)

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


def _safe_exists(p: Path) -> bool:
    """Like Path.exists() but returns False instead of raising PermissionError."""
    try:
        return p.exists()
    except (PermissionError, OSError):
        return False


def load_config(config_file: Path = None) -> MedicareConfig:
    """Load config from JSON file or return defaults."""
    if config_file is None:
        # Config file lives beside the user DB (writable location).
        config_file = _USER_DATA_ROOT / "config.json"
        # Fallback: check the old resource-root location so existing
        # developer machines with a checked-in config.json still work.
        if not _safe_exists(config_file):
            legacy = _RESOURCE_ROOT / "config.json"
            if _safe_exists(legacy):
                config_file = legacy
    if _safe_exists(config_file):
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
    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)
    except (PermissionError, OSError):
        pass  # Non-fatal — config is optional, defaults are always available

