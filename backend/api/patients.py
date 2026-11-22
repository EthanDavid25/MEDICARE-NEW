"""
API Router for Patient Profile & Registration.
Validates Indian mobile numbers (+91 / 10-digit formats).
"""
from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.patient import PatientCreateRequest, PatientResponse
from app.security.india_validation import validate_indian_mobile

router = APIRouter(prefix="/api/patients", tags=["Patients"])

def get_controller():
    from backend.main import get_app_controller
    return get_app_controller()

@router.post("", response_model=PatientResponse)
def register_or_update_patient(payload: PatientCreateRequest, controller=Depends(get_controller)):
    """
    Registers a new patient profile or updates an existing one.
    Strictly validates Indian mobile numbers (+91 or 10 digits starting with 6, 7, 8, or 9).
    """
    # Validate Indian phone number
    is_valid_phone, formatted_phone, error_msg = validate_indian_mobile(payload.phone_number)
    if not is_valid_phone:
        raise HTTPException(
            status_code=422,
            detail=error_msg or f"Invalid Indian mobile number: '{payload.phone_number}'."
        )

    # Validate emergency contact if provided
    formatted_emergency = None
    if payload.emergency_contact:
        is_valid_em, formatted_em, em_error = validate_indian_mobile(payload.emergency_contact)
        if not is_valid_em:
            raise HTTPException(
                status_code=422,
                detail=em_error or f"Invalid Indian emergency contact number: '{payload.emergency_contact}'."
            )
        formatted_emergency = formatted_em

    patient_data = {
        "display_name": payload.display_name.strip(),
        "phone_number": formatted_phone,
        "date_of_birth": payload.date_of_birth,
        "biological_sex": payload.biological_sex,
        "blood_group": payload.blood_group,
        "emergency_contact": formatted_emergency,
        "known_allergies": payload.known_allergies,
        "chronic_conditions": payload.chronic_conditions,
        "current_medications": payload.current_medications,
        "preferred_language": payload.preferred_language or "English"
    }

    patient_id = controller.patient_service.create_patient(patient_data)
    created_patient = controller.patient_service.get_patient(patient_id)

    return PatientResponse(
        id=created_patient.get("id"),
        display_name=created_patient.get("display_name", payload.display_name),
        phone_number=created_patient.get("phone_number", formatted_phone),
        date_of_birth=created_patient.get("date_of_birth"),
        age=payload.age,
        biological_sex=created_patient.get("biological_sex"),
        blood_group=created_patient.get("blood_group"),
        emergency_contact=created_patient.get("emergency_contact"),
        known_allergies=created_patient.get("known_allergies"),
        chronic_conditions=created_patient.get("chronic_conditions"),
        current_medications=created_patient.get("current_medications"),
        preferred_language=created_patient.get("preferred_language", "English"),
        created_at=created_patient.get("created_at")
    )

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, controller=Depends(get_controller)):
    """Retrieves a patient profile by ID."""
    patient = controller.patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(
        id=patient.get("id"),
        display_name=patient.get("display_name", "Patient"),
        phone_number=patient.get("phone_number"),
        date_of_birth=patient.get("date_of_birth"),
        biological_sex=patient.get("biological_sex"),
        blood_group=patient.get("blood_group"),
        emergency_contact=patient.get("emergency_contact"),
        known_allergies=patient.get("known_allergies"),
        chronic_conditions=patient.get("chronic_conditions"),
        current_medications=patient.get("current_medications"),
        preferred_language=patient.get("preferred_language", "English"),
        created_at=patient.get("created_at")
    )
