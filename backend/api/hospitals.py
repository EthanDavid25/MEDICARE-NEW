"""
API Router for Indian Healthcare Facilities and Hospital Finder.
Uses the verified Maharashtra healthcare directory and spatial grid service.
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Depends, HTTPException
from backend.schemas.hospital import FacilitySchema, FacilityListResponse
from app.healthcare.location_service import haversine_distance

router = APIRouter(prefix="/api/hospitals", tags=["Hospitals"])

def get_controller():
    from backend.main import get_app_controller
    return get_app_controller()

def get_active_facilities(controller) -> List[Dict[str, Any]]:
    """Loads verified Indian facilities if available, falling back to dataset loader."""
    india_file = Path(controller.config.data_dir) / "healthcare" / "facilities_india.json"
    if india_file.exists():
        try:
            with open(india_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return controller.dataset_loader.get_facilities()

@router.get("/nearby", response_model=FacilityListResponse)
def get_nearby_hospitals(
    latitude: Optional[float] = Query(None, description="Current latitude (e.g. 19.0760 for Mumbai)"),
    longitude: Optional[float] = Query(None, description="Current longitude (e.g. 72.8777 for Mumbai)"),
    locality: Optional[str] = Query(None, description="City, district or locality keyword (e.g. 'Dadar', 'Pune', 'Nagpur')"),
    radius_km: float = Query(25.0, ge=1.0, le=200.0),
    emergency_only: bool = Query(False, description="Filter for 24x7 emergency facilities only"),
    controller=Depends(get_controller)
):
    """
    Search healthcare facilities by GPS coordinates or locality query.
    Calculates direct distance in km and returns sorted facilities.
    """
    facilities = get_active_facilities(controller)
    results = []

    # Default coordinates to Mumbai center if neither location nor locality is passed
    search_lat = latitude
    search_lon = longitude

    if locality and (search_lat is None or search_lon is None):
        # Resolve locality coordinates from offline dataset
        loc_clean = locality.strip().lower()
        for f in facilities:
            if (loc_clean in f.get("city", "").lower() or
                loc_clean in f.get("locality", "").lower() or
                loc_clean in f.get("district", "").lower() or
                loc_clean in f.get("name", "").lower()):
                search_lat = f.get("latitude")
                search_lon = f.get("longitude")
                break

    # If coordinates are available, calculate spatial distances
    for f in facilities:
        if emergency_only and not f.get("has_emergency", False):
            continue

        item = dict(f)
        try:
            f_lat = float(f.get("latitude", 0))
            f_lon = float(f.get("longitude", 0))
        except (ValueError, TypeError):
            f_lat, f_lon = 0.0, 0.0

        if search_lat is not None and search_lon is not None and (f_lat != 0.0 or f_lon != 0.0):
            km, _ = haversine_distance(float(search_lat), float(search_lon), f_lat, f_lon)
            item["distance_km"] = round(km, 1)
        else:
            item["distance_km"] = None

        # Filter by locality substring if provided
        if locality:
            loc_lower = locality.strip().lower()
            matches = (
                loc_lower in f.get("name", "").lower() or
                loc_lower in f.get("locality", "").lower() or
                loc_lower in f.get("city", "").lower() or
                loc_lower in f.get("district", "").lower()
            )
            if not matches and (item["distance_km"] is None or item["distance_km"] > radius_km):
                continue

        results.append(item)

    # Sort by distance if available, otherwise by facility name
    if search_lat is not None and search_lon is not None:
        results.sort(key=lambda x: (x.get("distance_km") is None, x.get("distance_km", 9999)))
    else:
        results.sort(key=lambda x: x.get("name", ""))

    schema_list = []
    for r in results:
        schema_list.append(FacilitySchema(
            id=r.get("id", ""),
            name=r.get("name", ""),
            facility_type=r.get("facility_type", "General Hospital"),
            locality=r.get("locality", ""),
            city=r.get("city", ""),
            district=r.get("district", ""),
            state=r.get("state") or "Maharashtra",
            pincode=r.get("pincode", ""),
            latitude=r.get("latitude", 0.0),
            longitude=r.get("longitude", 0.0),
            phone=r.get("phone", "+91-112"),
            emergency_helpline=r.get("emergency_helpline", "112 / 102"),
            has_emergency=r.get("has_emergency", True),
            has_icu=r.get("has_icu", False),
            has_trauma_care=r.get("has_trauma_care", False),
            beds_count=r.get("beds_count", 0),
            ownership=r.get("ownership", "Government"),
            distance_km=r.get("distance_km")
        ))

    search_center = None
    if search_lat and search_lon:
        search_center = {"latitude": search_lat, "longitude": search_lon, "radius_km": radius_km}

    return FacilityListResponse(
        total=len(schema_list),
        facilities=schema_list,
        search_center=search_center
    )

@router.get("/{facility_id}", response_model=FacilitySchema)
def get_facility_by_id(facility_id: str, controller=Depends(get_controller)):
    """Returns details for a specific healthcare facility."""
    facilities = get_active_facilities(controller)
    for f in facilities:
        if f.get("id") == facility_id:
            return FacilitySchema(**f)
    raise HTTPException(status_code=404, detail="Facility not found")
