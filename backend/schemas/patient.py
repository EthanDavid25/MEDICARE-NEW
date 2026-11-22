"""
Pydantic Schemas for Patient Registration and Profile API.
"""
from typing import Optional
from pydantic import BaseModel, Field

class PatientCreateRequest(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., description="Indian phone number (+91 or 10 digits)")
    date_of_birth: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=125)
    biological_sex: Optional[str] = "unspecified"
    blood_group: Optional[str] = "Unknown"
    emergency_contact: Optional[str] = None
    known_allergies: Optional[str] = "None"
    chronic_conditions: Optional[str] = "None"
    current_medications: Optional[str] = "None"
    preferred_language: Optional[str] = "English"

class PatientResponse(BaseModel):
    id: int
    display_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    biological_sex: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    preferred_language: Optional[str] = "English"
    created_at: Optional[str] = None
