"""
MEDICARE Google Maps Integration Service.

Provides live nearby healthcare facility discovery using the Google Places API (New).
Falls back gracefully to the local offline directory when internet is unavailable or
the API key is not configured. Never sends patient symptoms, history or medical data
to Google — only location coordinates are transmitted.

API key security:
  - Keys are read from the GOOGLE_MAPS_API_KEY environment variable or .env file.
  - Keys are NEVER hardcoded in source or committed to version control.
  - Restrict your key to the Places API (New) and your app's bundle ID/IP in the
    Google Cloud Console to limit exposure risk.

Required Google Cloud APIs:
  - Places API (New)                 → nearby healthcare facility search
  - Geocoding API                    → manual address → coordinates
  - (Optional) Routes API            → driving time / distance matrix
"""
import os
import json
import logging
import urllib.request
import urllib.parse
from typing import Optional

logger = logging.getLogger("medicare.maps")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
_PLACE_DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"

# Fields requested from Places API — only location-related, no medical data sent.
_NEARBY_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.types,"
    "places.nationalPhoneNumber,"
    "places.internationalPhoneNumber,"
    "places.websiteUri,"
    "places.regularOpeningHours,"
    "places.currentOpeningHours,"
    "places.businessStatus,"
    "places.rating,"
    "places.userRatingCount"
)

# Healthcare-related Place types supported by the Places API (New)
_HEALTH_TYPES = [
    "hospital",
    "emergency_room_entrance",
    "doctor",
    "pharmacy",
    "medical_lab",
    "physiotherapist",
    "dentist",
    "health",
]

# Max radius for nearby search in metres (5 km default; max 50 km per API docs)
DEFAULT_SEARCH_RADIUS_M = 10000  # 10 km


def _get_api_key() -> Optional[str]:
    """
    Reads the Google Maps API key from the environment.
    Returns None if not configured — callers must handle gracefully.
    """
    # First try environment variable directly
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if key:
        return key

    # Try loading from .env file in project root (not committed to git)
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for env_path in env_paths:
        env_path = os.path.normpath(env_path)
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GOOGLE_MAPS_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and val not in ("your_api_key_here", "PASTE_KEY_HERE"):
                                logger.debug("Loaded Google Maps API key from .env file.")
                                return val
            except Exception as exc:
                logger.debug("Could not read .env: %s", exc)

    return None


class GoogleMapsService:
    """
    Live Google Maps healthcare facility search and geocoding.

    Usage::

        svc = GoogleMapsService()
        if svc.is_configured():
            results = svc.search_nearby_healthcare(lat, lon, radius_m=10000, urgency=1)
        else:
            # Fall back to offline local directory
            ...
    """

    def __init__(self):
        self._api_key: Optional[str] = _get_api_key()
        if self._api_key:
            logger.info("Google Maps API configured — live facility search enabled.")
        else:
            logger.info(
                "GOOGLE_MAPS_API_KEY not set — Google Maps features disabled. "
                "Using offline local facility directory as fallback."
            )

    def is_configured(self) -> bool:
        """Returns True if a usable API key is present."""
        return bool(self._api_key)

    def geocode_address(self, address: str) -> tuple[bool, float, float, str]:
        """
        Converts a human-readable address to (lat, lon) using the Geocoding API.

        Returns:
            (success, latitude, longitude, display_name)
        """
        if not self._api_key:
            return False, 0.0, 0.0, "API key not configured"

        if not address or not address.strip():
            return False, 0.0, 0.0, "Empty address provided"

        try:
            params = urllib.parse.urlencode({
                "address": address.strip(),
                "key": self._api_key,
            })
            url = f"{_GEOCODING_URL}?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "MEDICARE-Triage/1.0"})

            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            status = data.get("status", "UNKNOWN")
            if status != "OK":
                logger.warning("Geocoding failed with status: %s", status)
                return False, 0.0, 0.0, f"Address not found (status: {status})"

            result = data["results"][0]
            loc = result["geometry"]["location"]
            display = result.get("formatted_address", address)
            return True, float(loc["lat"]), float(loc["lng"]), display

        except Exception as exc:
            logger.warning("Geocoding request failed: %s", exc)
            return False, 0.0, 0.0, f"Network error: {exc}"

    def search_nearby_healthcare(
        self,
        lat: float,
        lon: float,
        radius_m: int = DEFAULT_SEARCH_RADIUS_M,
        urgency_category: int = 3,
        max_results: int = 20,
    ) -> tuple[bool, list[dict], str]:
        """
        Searches the Google Places API (New) for nearby healthcare facilities.

        Only the user's geographic coordinates are sent to Google. No symptoms,
        patient names, medical history or assessment responses are transmitted.

        Args:
            lat: User's latitude
            lon: User's longitude
            radius_m: Search radius in metres (default 10 km)
            urgency_category: 1=Emergency, 2=Urgent, 3=Routine, 4=Insufficient
            max_results: Maximum number of results to return

        Returns:
            (success, list_of_facilities, error_message_or_empty)
        """
        if not self._api_key:
            return False, [], "Google Maps API key not configured — using offline directory."

        # For emergency (category 1) expand radius to find any ER, and prioritize hospitals
        if urgency_category == 1:
            radius_m = max(radius_m, 25000)  # 25 km for emergencies

        # Select types based on urgency
        if urgency_category == 1:
            search_types = ["hospital", "emergency_room_entrance"]
        elif urgency_category == 2:
            search_types = ["hospital", "doctor", "health"]
        else:
            search_types = ["hospital", "doctor", "pharmacy", "health"]

        payload = {
            "includedTypes": search_types,
            "maxResultCount": min(max_results, 20),  # API max is 20 per call
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": float(radius_m),
                }
            },
            "rankPreference": "DISTANCE",
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                _PLACES_NEARBY_URL,
                data=body,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": _NEARBY_FIELD_MASK,
                    "User-Agent": "MEDICARE-Triage/1.0",
                },
            )

            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            raw_places = data.get("places", [])
            if not raw_places:
                return True, [], "No healthcare facilities found within search radius."

            facilities = []
            for place in raw_places:
                fac = _parse_place(place, lat, lon)
                if fac:
                    facilities.append(fac)

            # Sort by distance for all categories; emergency gets ER boosted first
            if urgency_category == 1:
                facilities.sort(key=lambda f: (
                    0 if f.get("has_emergency") else 1,
                    f.get("distance_km", 999),
                ))
            else:
                facilities.sort(key=lambda f: f.get("distance_km", 999))

            logger.info(
                "Google Maps search returned %d facilities near (%.4f, %.4f).",
                len(facilities), lat, lon,
            )
            return True, facilities[:max_results], ""

        except urllib.error.HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8")[:300]
            except Exception:
                pass
            logger.error("Google Maps HTTP %s: %s", exc.code, body_text)
            return False, [], f"Google Maps API error {exc.code}. Check API key and billing."

        except Exception as exc:
            logger.warning("Google Maps request failed: %s", exc)
            return False, [], f"Network error: {exc}"

    def get_directions_url(
        self,
        dest_lat: Optional[float],
        dest_lon: Optional[float],
        dest_name: str,
        origin_lat: Optional[float] = None,
        origin_lon: Optional[float] = None,
        place_id: Optional[str] = None,
    ) -> str:
        """
        Builds a Google Maps directions URL. Uses place_id when available for precision.
        Falls back to coordinate-based or name-based query.
        """
        if place_id:
            # Most accurate — links directly to the place
            dest_param = f"place_id:{place_id}"
        elif dest_lat is not None and dest_lon is not None:
            dest_param = f"{dest_lat},{dest_lon}"
        else:
            dest_param = urllib.parse.quote(dest_name)

        if origin_lat is not None and origin_lon is not None:
            return (
                f"https://www.google.com/maps/dir/?api=1"
                f"&origin={origin_lat},{origin_lon}"
                f"&destination={urllib.parse.quote(str(dest_param))}"
                f"&travelmode=driving"
            )
        else:
            return (
                f"https://www.google.com/maps/search/?api=1"
                f"&query={urllib.parse.quote(str(dest_param))}"
            )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_place(place: dict, user_lat: float, user_lon: float) -> Optional[dict]:
    """Converts a raw Places API (New) place object into a normalised facility dict."""
    try:
        display = place.get("displayName", {})
        name = display.get("text", "") if isinstance(display, dict) else str(display)
        if not name:
            return None

        location = place.get("location", {})
        lat = float(location.get("latitude", user_lat))
        lon = float(location.get("longitude", user_lon))

        from app.healthcare.location_service import haversine_distance
        km, miles = haversine_distance(user_lat, user_lon, lat, lon)

        # Determine if it has an emergency department based on place types
        types = place.get("types", [])
        has_emergency = (
            "emergency_room_entrance" in types
            or "hospital" in types
        )
        facility_type = _classify_facility_type(types)

        # Opening hours
        hours_info = place.get("currentOpeningHours") or place.get("regularOpeningHours") or {}
        is_open_now = hours_info.get("openNow", None)
        if is_open_now is True:
            hours_text = "Open Now"
        elif is_open_now is False:
            hours_text = "Currently Closed"
        else:
            hours_text = "Hours not available"

        # Weekday description if available
        weekday_text = hours_info.get("weekdayDescriptions", [])
        if weekday_text:
            hours_text += " — " + " | ".join(weekday_text[:2])

        return {
            "place_id": place.get("id", ""),
            "name": name,
            "address": place.get("formattedAddress", "Address not available"),
            "city": "",       # Extracted from formattedAddress if needed
            "state": "",
            "phone": (
                place.get("nationalPhoneNumber")
                or place.get("internationalPhoneNumber")
                or "Not listed"
            ),
            "website": place.get("websiteUri", ""),
            "facility_type": facility_type,
            "has_emergency": has_emergency,
            "operating_hours": hours_text,
            "latitude": lat,
            "longitude": lon,
            "distance_km": km,
            "distance_miles": miles,
            "rating": place.get("rating"),
            "rating_count": place.get("userRatingCount"),
            "business_status": place.get("businessStatus", ""),
            "is_verified": True,        # Live Google Maps data = verified
            "source": "google_maps",    # Clearly label data origin
        }
    except Exception as exc:
        logger.debug("Could not parse place: %s — %s", place.get("displayName"), exc)
        return None


def _classify_facility_type(types: list) -> str:
    """Returns a human-readable facility type from Google Places type list."""
    type_map = {
        "hospital": "Hospital",
        "emergency_room_entrance": "Emergency Department",
        "doctor": "Medical Clinic",
        "pharmacy": "Pharmacy",
        "medical_lab": "Diagnostic / Lab",
        "physiotherapist": "Physiotherapy Clinic",
        "dentist": "Dental Clinic",
        "health": "Healthcare Facility",
    }
    for t in types:
        if t in type_map:
            return type_map[t]
    return "Healthcare Provider"
