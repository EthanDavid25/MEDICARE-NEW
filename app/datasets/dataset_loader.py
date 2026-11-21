"""
MEDICARE local medical dataset loader and repository.
Loads structured datasets from local JSON and CSV files.
Maintains 100% offline access — no internet connection required.
"""
import json
import csv
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("medicare.datasets")

class DatasetLoader:
    """Manages loading, parsing, searching and caching of medical datasets."""
    
    def __init__(self, data_dir: Path | str = None, db = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent.parent / "data"
        self.medical_dir = self.data_dir / "medical"
        self.healthcare_dir = self.data_dir / "healthcare"
        self.db = db
        self._symptoms: list[dict] = []
        self._warning_signs: list[dict] = []
        self._followup_questions: list[dict] = []
        self._risk_factors: list[dict] = []
        self._triage_rules: list[dict] = []
        self._medical_references: list[dict] = []
        self._facilities: list[dict] = []
        self._metadata: dict[str, dict] = {}
        self.load_all()

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            logger.warning("Dataset file missing: %s", path)
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to parse JSON dataset %s: %s", path.name, e)
            return {}

    def load_all(self):
        """Loads all local datasets into memory."""
        # 1. Symptoms
        sym_data = self._read_json(self.medical_dir / "symptoms.json")
        self._symptoms = sym_data.get("symptoms", [])
        if "metadata" in sym_data:
            self._metadata["symptoms"] = sym_data["metadata"]

        # 2. Warning Signs
        warn_data = self._read_json(self.medical_dir / "warning_signs.json")
        self._warning_signs = warn_data.get("warning_signs", [])
        if "metadata" in warn_data:
            self._metadata["warning_signs"] = warn_data["metadata"]

        # 3. Followup Questions
        q_data = self._read_json(self.medical_dir / "followup_questions.json")
        self._followup_questions = q_data.get("questions", [])
        if "metadata" in q_data:
            self._metadata["followup_questions"] = q_data["metadata"]

        # 4. Risk Factors
        rf_data = self._read_json(self.medical_dir / "risk_factors.json")
        self._risk_factors = rf_data.get("risk_factors", [])
        if "metadata" in rf_data:
            self._metadata["risk_factors"] = rf_data["metadata"]

        # 5. Triage Rules
        rule_data = self._read_json(self.medical_dir / "triage_rules.json")
        self._triage_rules = rule_data.get("rules", [])
        if "metadata" in rule_data:
            self._metadata["triage_rules"] = rule_data["metadata"]

        # 6. Medical References
        ref_data = self._read_json(self.medical_dir / "medical_references.json")
        self._medical_references = ref_data.get("references", [])
        if "metadata" in ref_data:
            self._metadata["medical_references"] = ref_data["metadata"]

        # 7. Healthcare Facilities
        self._load_facilities_csv()

        logger.info(
            "Datasets loaded: %d symptoms, %d warning signs, %d questions, %d rules, %d references, %d facilities",
            len(self._symptoms), len(self._warning_signs), len(self._followup_questions),
            len(self._triage_rules), len(self._medical_references), len(self._facilities)
        )

    def _load_facilities_csv(self):
        csv_path = self.healthcare_dir / "facilities.csv"
        if not csv_path.exists():
            logger.warning("Facilities CSV missing: %s", csv_path)
            self._facilities = []
            return
        facilities = []
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(row for row in f if not row.strip().startswith("#"))
                for row in reader:
                    facilities.append(dict(row))
            self._facilities = facilities
        except Exception as e:
            logger.error("Failed to load facilities CSV: %s", e)
            self._facilities = []

    def get_symptoms(self) -> list[dict]:
        return self._symptoms

    def search_symptoms(self, query: str) -> list[dict]:
        """Filters symptoms by code, name, or aliases."""
        if not query:
            return self._symptoms
        q = query.lower().strip()
        matched = []
        for s in self._symptoms:
            name = s.get("name", "").lower()
            code = s.get("code", "").lower()
            aliases = [a.lower() for a in s.get("aliases", [])]
            body_system = s.get("body_system", "").lower()
            if q in name or q in code or any(q in a for a in aliases) or q in body_system:
                matched.append(s)
        return matched

    def get_warning_signs(self) -> list[dict]:
        return self._warning_signs

    def get_followup_questions_for_symptoms(self, symptom_codes: list[str]) -> list[dict]:
        """Finds relevant follow-up questions linked to selected symptoms, plus general questions."""
        codes_set = set(symptom_codes)
        matched = []
        seen = set()
        for q in self._followup_questions:
            qid = q.get("question_id")
            if qid in seen:
                continue
            q_syms = set(q.get("symptom_codes", []))
            if "ALL" in q_syms or bool(q_syms.intersection(codes_set)):
                matched.append(q)
                seen.add(qid)
        return matched

    def get_risk_factors(self) -> list[dict]:
        return self._risk_factors

    def get_triage_rules(self) -> list[dict]:
        return self._triage_rules

    def get_medical_references(self, category: str = None) -> list[dict]:
        if not category or category == "ALL":
            return self._medical_references
        return [r for r in self._medical_references if r.get("category") == category]

    def get_facilities(self, filter_type: str = "ALL", emergency_only: bool = False, search: str = "") -> list[dict]:
        results = []
        q = search.lower().strip() if search else ""
        for fac in self._facilities:
            if emergency_only and str(fac.get("has_emergency", "0")) != "1":
                continue
            ft = fac.get("facility_type", "")
            if filter_type != "ALL" and ft != filter_type:
                continue
            if q:
                searchable = f"{fac.get('name', '')} {fac.get('city', '')} {fac.get('services', '')} {fac.get('address', '')}".lower()
                if q not in searchable:
                    continue
            results.append(fac)
        return results

    def get_metadata(self) -> dict[str, dict]:
        return self._metadata
