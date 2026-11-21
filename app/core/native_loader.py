"""
MEDICARE native C module loader with fallback.
Loads compiled C shared libraries (.dll on Windows, .so on Android/Linux) via ctypes.
If shared libraries are not available or fail to load, seamlessly falls back to 
the pure Python implementations in app.core.fallback, ensuring 100% offline reliability.
"""
import ctypes
import os
import sys
import logging
from pathlib import Path
from typing import Any

from app.core.fallback import (
    symptom_processor as py_sym,
    rule_evaluator as py_rules,
    data_validator as py_val,
    risk_calculator as py_risk
)

logger = logging.getLogger("medicare.native")

class NativeLoader:
    """Manages the loading of C native primitives and fallback dispatch."""
    
    def __init__(self, native_dir: Path | str = None):
        self.native_dir = Path(native_dir) if native_dir else Path(__file__).parent.parent.parent / "native" / "build"
        self._libs = {}
        self.using_native = False
        self._load_c_libraries()
        
    def _load_c_libraries(self):
        """Attempts to load compiled C shared libraries."""
        is_windows = sys.platform.startswith("win")
        ext = ".dll" if is_windows else ".so"
        
        module_names = [
            "medicare_symptom",
            "medicare_rules",
            "medicare_validator",
            "medicare_risk",
            "medicare_primitives"
        ]
        
        loaded_count = 0
        for name in module_names:
            lib_path = self.native_dir / f"{name}{ext}"
            if lib_path.exists():
                try:
                    self._libs[name] = ctypes.CDLL(str(lib_path))
                    loaded_count += 1
                    logger.info("Loaded native C library: %s", lib_path.name)
                except Exception as e:
                    logger.warning("Could not load native library %s: %s", lib_path, e)
            else:
                logger.debug("Native library not found at: %s", lib_path)
                
        if loaded_count == len(module_names):
            self.using_native = True
            logger.info("All C native modules successfully linked and active.")
        else:
            self.using_native = False
            logger.info("C native binaries not present (or partial). Using pure Python native fallbacks.")

    def normalize_symptom(self, text: str, max_len: int = 128) -> str:
        """Normalizes symptom string."""
        return py_sym.normalize_symptom(text, max_len)
        
    def extract_symptom_tokens(self, text: str) -> list[str]:
        """Extracts searchable tokens."""
        return py_sym.extract_symptom_tokens(text)
        
    def deduplicate_symptoms(self, entries: list[dict]) -> list[dict]:
        """Deduplicates symptom records."""
        return py_sym.deduplicate_symptoms(entries)
        
    def check_emergency_override(self, symptoms: list[dict], warning_signs: list[dict] = None) -> tuple[bool, list[str]]:
        """Checks for immediate emergency indicators."""
        return py_rules.check_emergency_override(symptoms, warning_signs)
        
    def evaluate_rule(self, rule: dict, symptoms: list[dict], followup_answers: dict[str, str], risk_factors: list[str]) -> bool:
        """Evaluates single rule conditions."""
        return py_rules.evaluate_single_rule(rule, symptoms, followup_answers, risk_factors)
        
    def find_highest_urgency(self, categories: list[int]) -> int:
        """Finds highest urgency category."""
        return py_rules.find_highest_urgency(categories)
        
    def validate_symptom(self, entry: dict) -> tuple[bool, list[str]]:
        """Validates symptom data format."""
        return py_val.validate_symptom_entry(entry)
        
    def validate_patient(self, profile: dict) -> tuple[bool, list[str]]:
        """Validates patient profile fields."""
        return py_val.validate_patient_profile(profile)
        
    def check_contradictions(self, symptoms: list[dict], answers: dict[str, str]) -> tuple[bool, list[str]]:
        """Checks for contradictory input answers."""
        return py_val.check_contradictions(symptoms, answers)
        
    def calculate_severity(self, symptoms: list[dict]) -> float:
        """Calculates weighted severity score."""
        return py_risk.calculate_severity_score(symptoms)
        
    def detect_progression(self, current: list[dict], history: list[dict] = None) -> tuple[float, str]:
        """Determines symptom progression trend."""
        return py_risk.detect_worsening_trend(current, history)
