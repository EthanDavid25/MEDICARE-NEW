"""MEDICARE application configuration management."""
from dataclasses import dataclass, field
from pathlib import Path
import json
import os

APP_ROOT = Path(__file__).parent.parent.parent

@dataclass
class MedicareConfig:
    app_name: str = "MEDICARE"
    app_version: str = "1.0.0"
    app_root: Path = field(default_factory=lambda: APP_ROOT)
    db_path: Path = field(default_factory=lambda: APP_ROOT / "data" / "database" / "medicare.db")
    log_path: Path = field(default_factory=lambda: APP_ROOT / "logs" / "medicare.log")
    data_dir: Path = field(default_factory=lambda: APP_ROOT / "data")
    medical_data_dir: Path = field(default_factory=lambda: APP_ROOT / "data" / "medical")
    healthcare_data_dir: Path = field(default_factory=lambda: APP_ROOT / "data" / "healthcare")
    native_dir: Path = field(default_factory=lambda: APP_ROOT / "native" / "build")
    encryption_enabled: bool = False
    offline_mode: bool = True
    triage_version: str = "1.0.0"
    log_level: str = "INFO"

    def ensure_directories(self):
        """Create required directories if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        return {k: str(v) if isinstance(v, Path) else v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "MedicareConfig":
        path_fields = {
            "app_root", "db_path", "log_path", "data_dir",
            "medical_data_dir", "healthcare_data_dir", "native_dir",
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
        config_file = APP_ROOT / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return MedicareConfig.from_dict(data)
        except Exception:
            pass
    return MedicareConfig()


def save_config(config: MedicareConfig, config_file: Path = None):
    """Save config to JSON file."""
    if config_file is None:
        config_file = APP_ROOT / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)
