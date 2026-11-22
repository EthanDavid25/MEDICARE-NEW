"""
API Router for Clinical Doctor Handover PDF Reports.
Generates ReportLab PDF summaries offline and serves them for mobile download.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.reports.handover_pdf import generate_doctor_handover_pdf

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def get_controller():
    from backend.main import get_app_controller
    return get_app_controller()

class HandoverGenerateRequest(BaseModel):
    session_id: str
    patient_id: Optional[int] = 1
    triage_result: Dict[str, Any]

class HandoverGenerateResponse(BaseModel):
    session_id: str
    pdf_filename: str
    download_url: str
    file_size_bytes: int

@router.post("/handover", response_model=HandoverGenerateResponse)
def create_handover_pdf(payload: HandoverGenerateRequest, controller=Depends(get_controller)):
    """
    Generates a structured, professional clinical Doctor Handover PDF summary using ReportLab.
    Retains full technical details (unanswered safety questions, technical rule names, scores, actions).
    """
    patient = controller.patient_service.get_patient(payload.patient_id or 1)
    if not patient:
        patient = {
            "display_name": "Anonymous Patient",
            "date_of_birth": "Not specified",
            "biological_sex": "unspecified",
            "blood_group": "Unknown"
        }

    out_dir = Path(controller.config.data_dir) / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = f"Handover_{payload.session_id}.pdf"
    out_file = out_dir / pdf_filename

    # Generate PDF using existing authoritative generator
    generate_doctor_handover_pdf(patient, payload.triage_result, out_file)

    if not out_file.exists():
        raise HTTPException(status_code=500, detail="Failed to generate Doctor Handover PDF.")

    # Register with handover service library tracking
    symptoms = payload.triage_result.get("symptoms", [])
    symptoms_str = ", ".join(s.get("name", "") for s in symptoms) if symptoms else "Reported symptoms"
    
    try:
        controller.handover_service.register_download(
            session_id=payload.session_id,
            patient_id=payload.patient_id or 1,
            patient_name=patient.get("display_name", "Anonymous Patient"),
            title=f"Doctor Handover — {payload.session_id}",
            main_symptoms=symptoms_str,
            pain_severity=payload.triage_result.get("severity_score", 5.0),
            triage_category=payload.triage_result.get("urgency_category", 3),
            triage_label=payload.triage_result.get("urgency_label", "Routine Healthcare"),
            file_path=out_file
        )
    except Exception:
        pass

    return HandoverGenerateResponse(
        session_id=payload.session_id,
        pdf_filename=pdf_filename,
        download_url=f"/api/reports/download/{pdf_filename}",
        file_size_bytes=out_file.stat().st_size
    )

@router.get("/download/{filename}")
def download_pdf(filename: str, controller=Depends(get_controller)):
    """Downloads a generated PDF report file."""
    # Prevent directory traversal attacks
    safe_name = Path(filename).name
    file_path = Path(controller.config.data_dir) / "reports" / safe_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested report PDF not found.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name
    )
