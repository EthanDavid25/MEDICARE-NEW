"""
MEDICARE Patient Assessment History and Progression Tracking Service.
Provides chronological timeline queries, progression tracking, symptom comparisons,
and detects symptom worsening across distinct evaluation dates.
"""
import json
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger("medicare.history")

class HistoryService:
    def __init__(self, db):
        self.db = db

    def get_assessment_history(self, patient_id: int, limit: int = 50) -> list[dict]:
        """Returns ordered list of prior assessments for the specified patient."""
        return self.db.fetchall(
            "SELECT * FROM assessments WHERE patient_id = ? AND is_deleted = 0 ORDER BY completed_at DESC LIMIT ?",
            (patient_id, limit)
        )

    def get_assessment_detail(self, assessment_id: int) -> Optional[dict]:
        """Returns single assessment record with its symptom entries and follow-up answers."""
        assessment = self.db.fetchone("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
        if not assessment:
            return None
        entries = self.db.fetchall("SELECT * FROM symptom_entries WHERE assessment_id = ?", (assessment_id,))
        answers = self.db.fetchall("SELECT * FROM followup_answers WHERE assessment_id = ?", (assessment_id,))
        
        detail = dict(assessment)
        detail["symptoms"] = entries
        detail["followup_answers"] = answers
        return detail

    def get_symptom_progression_timeline(self, patient_id: int, symptom_code: str = None) -> list[dict]:
        """
        Retrieves historical symptom records for progression visualization and charts.
        Can filter by specific symptom code or return entire chronological timeline.
        """
        if symptom_code:
            return self.db.fetchall(
                "SELECT * FROM symptom_history WHERE patient_id = ? AND symptom_code = ? ORDER BY recorded_at ASC",
                (patient_id, symptom_code)
            )
        else:
            return self.db.fetchall(
                "SELECT * FROM symptom_history WHERE patient_id = ? ORDER BY recorded_at ASC",
                (patient_id,)
            )

    def compare_assessments(self, previous_assessment_id: int, current_assessment_id: int) -> dict:
        """
        Compares two distinct assessment records to evaluate changes in severity,
        new symptoms emerged, or urgency trajectory changes.
        """
        prev = self.get_assessment_detail(previous_assessment_id)
        curr = self.get_assessment_detail(current_assessment_id)
        
        if not prev or not curr:
            return {}

        prev_sym_map = {s["symptom_code"]: s for s in prev.get("symptoms", [])}
        curr_sym_map = {s["symptom_code"]: s for s in curr.get("symptoms", [])}

        worsened = []
        improved = []
        new_symptoms = []
        resolved = []

        for code, curr_s in curr_sym_map.items():
            if code in prev_sym_map:
                diff = curr_s.get("severity", 0) - prev_sym_map[code].get("severity", 0)
                if diff > 0:
                    worsened.append({"name": curr_s.get("symptom_name"), "delta": diff})
                elif diff < 0:
                    improved.append({"name": curr_s.get("symptom_name"), "delta": diff})
            else:
                new_symptoms.append({"name": curr_s.get("symptom_name"), "severity": curr_s.get("severity")})

        for code, prev_s in prev_sym_map.items():
            if code not in curr_sym_map:
                resolved.append({"name": prev_s.get("symptom_name")})

        urgency_change = "unchanged"
        if curr.get("urgency_category", 3) < prev.get("urgency_category", 3):
            urgency_change = "escalated_urgency"
        elif curr.get("urgency_category", 3) > prev.get("urgency_category", 3):
            urgency_change = "deescalated_urgency"

        return {
            "previous_date": prev.get("completed_at"),
            "current_date": curr.get("completed_at"),
            "urgency_change": urgency_change,
            "previous_category": prev.get("urgency_category"),
            "current_category": curr.get("urgency_category"),
            "worsened": worsened,
            "improved": improved,
            "new_symptoms": new_symptoms,
            "resolved": resolved
        }
