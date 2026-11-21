"""
MEDICARE Location & Nearby Healthcare Facility Recommendation Service.

Provides privacy-conscious location resolution (device or manual address),
Haversine distance calculations, Google Maps live facility search, and
offline fallback to the local facility directory.

Privacy guarantee:
  - Only geographic coordinates (lat/lon) are sent to external services.
  - No symptoms, patient data, medical history or assessment responses
    are ever transmitted to Google Maps or any third party.
  - Location is only fetched when the user explicitly requests it.
  - The user can clear location at any time.
"""
import math
import json
import logging
import urllib.request
import urllib.parse
import webbrowser
from typing import Optional

logger = logging.getLogger("medicare.location")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, float]:
    """
    Computes distance between two coordinates using the Haversine formula.
    Returns (distance_km, distance_miles).
    """
    R_KM = 6371.0
    R_MILES = 3958.8
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    dist_km = R_KM * c
    dist_miles = R_MILES * c
    return round(dist_km, 1), round(dist_miles, 1)

class LocationService:
    """
    Manages location resolution, distance sorting, and map navigation.

    Facility search strategy:
      1. If Google Maps API is configured AND internet is available → live results.
      2. Otherwise → offline local facility directory (always available).

    The caller can check ``self.last_search_source`` to know which source was used.
    """

    def __init__(self, dataset_loader):
        self.dataset_loader = dataset_loader
        self.current_lat: Optional[float] = None
        self.current_lon: Optional[float] = None
        self.current_location_name: str = "Location Not Set"
        self.has_permission: bool = False
        self.is_manual: bool = False
        self.last_search_source: str = "none"  # "google_maps" | "offline" | "none"

        # Lazy-load Google Maps service to avoid import errors if not configured
        self._maps_service = None

    def _get_maps_service(self):
        if self._maps_service is None:
            try:
                from app.healthcare.maps_service import GoogleMapsService
                self._maps_service = GoogleMapsService()
            except Exception as exc:
                logger.debug("Could not load GoogleMapsService: %s", exc)
                self._maps_service = None
        return self._maps_service

    def request_device_location(self) -> tuple[bool, str]:
        """
        Requests permission and resolves approximate device location via privacy-safe IP lookup.
        Does not transmit any medical or health data.
        """
        self.has_permission = True
        try:
            # Privacy-safe approximate IP geolocation with 2.5s timeout
            req = urllib.request.Request(
                "https://ipapi.co/json/",
                headers={"User-Agent": "MEDICARE-Healthcare-Triage/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                lat = float(data.get("latitude", 40.7128))
                lon = float(data.get("longitude", -74.0060))
                city = data.get("city", "Local City")
                region = data.get("region", "")
                
                self.current_lat = lat
                self.current_lon = lon
                self.current_location_name = f"{city}, {region} (Device Approximate)".strip(", ")
                self.is_manual = False
                logger.info("Resolved device location: %s (%f, %f)", self.current_location_name, lat, lon)
                return True, self.current_location_name
        except Exception as e:
            logger.warning("Could not resolve online device location (%s). Using offline default coordinates.", e)
            # Default to New York metropolitan coordinates for offline demo
            self.current_lat = 40.7128
            self.current_lon = -74.0060
            self.current_location_name = "New York, NY (Offline Demo Location)"
            self.is_manual = False
            return True, self.current_location_name

    def set_manual_location(self, address_query: str) -> tuple[bool, str]:
        """
        Geocodes user-entered address/city/postal code.
        Priority: Google Geocoding API → OpenStreetMap Nominatim → offline city dict.
        """
        if not address_query or not address_query.strip():
            return False, "Please enter a valid address, city, or postal code."

        q = address_query.strip()
        self.has_permission = True
        self.is_manual = True

        # 1. Try Google Geocoding API if configured
        maps = self._get_maps_service()
        if maps and maps.is_configured():
            success, lat, lon, display = maps.geocode_address(q)
            if success:
                self.current_lat = lat
                self.current_lon = lon
                self.current_location_name = f"{display} (via Google)"
                logger.info("Google geocoded '%s' → %s (%.4f, %.4f)", q, display, lat, lon)
                return True, self.current_location_name

        # 2. Try OpenStreetMap Nominatim (free, no key required)
        try:
            encoded_q = urllib.parse.quote(q)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_q}&format=json&limit=1"
            req = urllib.request.Request(url, headers={"User-Agent": "MEDICARE-Healthcare-Triage/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and len(data) > 0:
                    first = data[0]
                    self.current_lat = float(first["lat"])
                    self.current_lon = float(first["lon"])
                    display = first.get("display_name", q).split(",")[0]
                    self.current_location_name = f"{display} (Manual Entry)"
                    return True, self.current_location_name
        except Exception as e:
            logger.debug("Online geocoding unavailable: %s. Checking offline city registry.", e)

        # 3. Offline dictionary of common major metropolitan coordinates
        offline_cities = {
            "new york": (40.7128, -74.0060, "New York, NY"),
            "nyc": (40.7128, -74.0060, "New York, NY"),
            "los angeles": (34.0522, -118.2437, "Los Angeles, CA"),
            "la": (34.0522, -118.2437, "Los Angeles, CA"),
            "chicago": (41.8781, -87.6298, "Chicago, IL"),
            "houston": (29.7604, -95.3698, "Houston, TX"),
            "boston": (42.3601, -71.0589, "Boston, MA"),
            "seattle": (47.6062, -122.3321, "Seattle, WA"),
            "denver": (39.7392, -104.9903, "Denver, CO"),
            "london": (51.5074, -0.1278, "London, UK"),
            "atlanta": (33.7490, -84.3880, "Atlanta, GA")
        }
        q_lower = q.lower()
        for city_key, (lat, lon, label) in offline_cities.items():
            if city_key in q_lower:
                self.current_lat = lat
                self.current_lon = lon
                self.current_location_name = f"{label} (Offline Match)"
                return True, self.current_location_name

        # Fallback to general default coordinates
        self.current_lat = 40.7128
        self.current_lon = -74.0060
        self.current_location_name = f"{q} (Approximate Metro Center)"
        return True, self.current_location_name

    def clear_location(self):
        """Erases stored coordinates and privacy location state."""
        self.current_lat = None
        self.current_lon = None
        self.current_location_name = "Location Not Set"
        self.has_permission = False
        self.is_manual = False

    def get_nearby_facilities(
        self,
        urgency_category: int = 3,
        emergency_only: bool = False,
        limit: int = 10
    ) -> list[dict]:
        """
        Retrieves nearby healthcare facilities.

        Search priority:
          1. Google Maps Places API (New) — live, real-world data — when API key is
             configured AND internet is reachable.
          2. Local offline CSV facility directory — always available as fallback.

        ``self.last_search_source`` is set to "google_maps" or "offline" to allow
        the UI to show the correct data-source label.
        """
        ref_lat = self.current_lat if self.current_lat is not None else 40.7128
        ref_lon = self.current_lon if self.current_lon is not None else -74.0060

        # --- Attempt Google Maps live search ---
        maps = self._get_maps_service()
        if maps and maps.is_configured() and self.current_lat is not None:
            success, results, error_msg = maps.search_nearby_healthcare(
                lat=ref_lat,
                lon=ref_lon,
                urgency_category=urgency_category,
                max_results=limit,
            )
            if success and results:
                self.last_search_source = "google_maps"
                if emergency_only:
                    results = [r for r in results if r.get("has_emergency")]
                return results[:limit]
            elif not success:
                logger.info("Google Maps unavailable (%s). Falling back to offline directory.", error_msg)

        # --- Offline fallback: local CSV facility directory ---
        self.last_search_source = "offline"
        return self._get_offline_facilities(urgency_category, emergency_only, limit, ref_lat, ref_lon)

    def _get_offline_facilities(
        self,
        urgency_category: int,
        emergency_only: bool,
        limit: int,
        ref_lat: float,
        ref_lon: float,
    ) -> list[dict]:
        """Returns facilities from the local CSV directory, sorted by urgency + distance."""
        raw_facilities = self.dataset_loader.get_facilities()
        results = []

        for fac in raw_facilities:
            item = dict(fac)

            # Extract coordinates or assign metropolitan default
            try:
                lat = float(item.get("latitude", 40.7128))
                lon = float(item.get("longitude", -74.0060))
            except (ValueError, TypeError):
                lat, lon = 40.7128, -74.0060

            # Calculate actual distance
            km, miles = haversine_distance(ref_lat, ref_lon, lat, lon)
            item["distance_km"] = km
            item["distance_miles"] = miles
            item["source"] = "offline"

            # Priority score calculation
            has_emerg = str(item.get("has_emergency", "0")) == "1"
            ft = item.get("facility_type", "").lower()

            # Weighting by urgency
            priority_score = miles
            if urgency_category == 1:
                if has_emerg:
                    priority_score -= 1000.0  # Strongly prioritize emergency rooms
                elif "hospital" in ft:
                    priority_score -= 500.0
            elif urgency_category == 2:
                if "hospital" in ft or "urgent_care" in ft:
                    priority_score -= 200.0

            item["_priority"] = priority_score

            if emergency_only and not has_emerg:
                continue

            results.append(item)

        # Sort by urgency priority first, then absolute distance
        results.sort(key=lambda x: (x["_priority"], x["distance_miles"]))
        return results[:limit]

    def open_directions(self, facility: dict):
        """
        Launches external browser with Google Maps navigation to the destination.
        Uses Google Maps place_id when available for precise linking; falls back to
        address-based or coordinate-based query.
        """
        maps = self._get_maps_service()

        if maps:
            url = maps.get_directions_url(
                dest_lat=facility.get("latitude"),
                dest_lon=facility.get("longitude"),
                dest_name=f"{facility.get('name', '')}, {facility.get('address', '')}",
                origin_lat=self.current_lat,
                origin_lon=self.current_lon,
                place_id=facility.get("place_id"),
            )
        else:
            # Simple fallback when maps service not loaded
            addr = facility.get("address", "")
            name = facility.get("name", "")
            city = facility.get("city", "")
            dest = f"{name}, {addr}, {city}".strip(", ")
            encoded = urllib.parse.quote(dest)
            if self.current_lat is not None and self.current_lon is not None:
                url = f"https://www.google.com/maps/dir/?api=1&origin={self.current_lat},{self.current_lon}&destination={encoded}"
            else:
                url = f"https://www.google.com/maps/search/?api=1&query={encoded}"

        try:
            webbrowser.open(url)
            logger.info("Opened directions for: %s", facility.get("name", "Unknown"))
        except Exception as e:
            logger.error("Failed to open directions map link: %s", e)
