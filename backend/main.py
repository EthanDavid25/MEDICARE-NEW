"""
MEDICARE Mobile Backend API Entry Point.
Exposes the authoritative MEDICARE clinical engine, adaptive questionnaire,
Maharashtra healthcare directory, and ReportLab PDF generator via FastAPI.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safe fallback for MEDICARE_DATA_HOME if local appdata isn't accessible
if "MEDICARE_DATA_HOME" not in os.environ:
    os.environ["MEDICARE_DATA_HOME"] = str(Path(os.environ.get("TEMP", "/tmp")) / "medicare_data")

from app.core.config import load_config
from app.core.app_controller import AppController

_controller: AppController = None

def get_app_controller() -> AppController:
    global _controller
    if _controller is None:
        config = load_config()
        _controller = AppController(config)
        _controller.initialize()
    return _controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the authoritative controller
    ctrl = get_app_controller()
    yield
    # Shutdown: Cleanly close DB and resources
    if _controller:
        _controller.shutdown()

app = FastAPI(
    title="MEDICARE Clinical API",
    description="Authoritative medical symptoms triage and clinical decision-support API for MEDICARE Mobile.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for mobile development / React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
from backend.api.assessment import router as assessment_router
from backend.api.hospitals import router as hospitals_router
from backend.api.patients import router as patients_router
from backend.api.reports import router as reports_router
from backend.api.sync import router as sync_router

app.include_router(assessment_router)
app.include_router(hospitals_router)
app.include_router(patients_router)
app.include_router(reports_router)
app.include_router(sync_router)

@app.get("/health")
def health_check():
    """Service health and clinical engine status check."""
    ctrl = get_app_controller()
    loader = ctrl.dataset_loader
    return {
        "status": "healthy",
        "app_name": "MEDICARE",
        "version": ctrl.config.app_version,
        "clinical_engine": "MEDICARE_AUTHORITATIVE_v1.0.0",
        "datasets": {
            "symptoms_count": len(loader.get_symptoms()),
            "rules_count": len(loader.get_triage_rules()),
            "warning_signs_count": len(loader.get_warning_signs()),
            "questions_count": len(loader.get_followup_questions()),
            "facilities_count": len(loader.get_facilities())
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
