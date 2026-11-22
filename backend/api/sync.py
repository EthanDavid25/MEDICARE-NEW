"""
API Router for Offline Dataset Synchronization.
Bundles all verified medical datasets, questions, rules, and Maharashtra facilities.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.api.hospitals import get_active_facilities

router = APIRouter(prefix="/api/sync", tags=["Sync"])

def get_controller():
    from backend.main import get_app_controller
    return get_app_controller()

@router.get("/bundle")
def get_offline_sync_bundle(controller=Depends(get_controller)) -> Dict[str, Any]:
    """
    Returns the complete bundle of authoritative medical datasets:
    - 81 symptoms
    - 28 concise (<=7 word) follow-up questions
    - 22 triage rules
    - 40 warning signs
    - Verified Maharashtra healthcare facilities
    Allows the mobile client to run 100% offline with zero network connectivity.
    """
    loader = controller.dataset_loader
    return {
        "version": "1.0.0",
        "symptoms": loader.get_symptoms(),
        "followup_questions": loader.get_followup_questions(),
        "triage_rules": loader.get_triage_rules(),
        "warning_signs": loader.get_warning_signs(),
        "facilities": get_active_facilities(controller),
        "synced_at": "2026-11-22T00:00:00Z"
    }
