"""
Pydantic Schemas for Healthcare Facilities API.
"""
from typing import Optional, List
from pydantic import BaseModel

class FacilitySchema(BaseModel):
    id: str
    name: str
    facility_type: str
    locality: str
    city: str
    district: str
    state: str = "Maharashtra"
    pincode: str
    latitude: float
    longitude: float
    phone: str
    emergency_helpline: Optional[str] = "112 / 102"
    has_emergency: bool = True
    has_icu: bool = False
    has_trauma_care: bool = False
    beds_count: Optional[int] = 0
    ownership: str = "Government"
    distance_km: Optional[float] = None

class FacilityListResponse(BaseModel):
    total: int
    facilities: List[FacilitySchema]
    search_center: Optional[dict] = None
