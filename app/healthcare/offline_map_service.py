"""
MEDICARE Offline Map & Geographic Service.

Coordinates:
- Map tile calculations & in-memory caching
- 2D Spatial Grid indexing for nearby hospital lookups
- Offline road graph A* routing to nearest emergency departments
- Maharashtra regional boundary validation
- MBTiles container inspection
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from app.healthcare.native_map_loader import (
    get_native_map_loader,
    PythonMapEngine,
    PythonTileCache,
    PythonSpatialGridIndex,
    PythonRoadGraph,
    TileCoord,
    GeoPoint
)

logger = logging.getLogger("medicare.map_service")

class OfflineMapService:
    """Manages offline map tiles, spatial queries, and local routing."""

    def __init__(self, dataset_loader):
        self.dataset_loader = dataset_loader
        self.loader = get_native_map_loader()
        self.tile_cache = PythonTileCache(max_entries=256, max_bytes=32 * 1024 * 1024)
        self.spatial_index: Optional[PythonSpatialGridIndex] = None
        self.road_graph: Optional[PythonRoadGraph] = None
        self._build_spatial_index()
        self._build_default_road_graph()

    def _build_spatial_index(self):
        """Indexes all local facilities into the 2D spatial grid."""
        raw_facilities = self.dataset_loader.get_facilities()
        # Initialize grid covering Maharashtra / India metropolitan areas
        self.spatial_index = PythonSpatialGridIndex(
            min_lat=8.0, min_lon=68.0, max_lat=36.0, max_lon=98.0, cell_size_km=15.0
        )
        count = 0
        for f in raw_facilities:
            try:
                item = dict(f)
                item["latitude"] = float(f.get("latitude", 19.0760))
                item["longitude"] = float(f.get("longitude", 72.8777))
                item["has_emergency"] = str(f.get("has_emergency", "0")) in ("1", "True", "true")
                self.spatial_index.insert(item)
                count += 1
            except Exception as e:
                logger.debug("Could not index facility: %s", e)
        logger.info("Spatial grid indexed %d facilities for O(1) nearby queries.", count)

    def _build_default_road_graph(self):
        """Builds a connected reference road graph for Maharashtra emergency routing."""
        self.road_graph = PythonRoadGraph()

        # Key landmark intersections across Mumbai / Pune / Maharashtra highway corridors
        nodes = [
            (101, 18.9220, 72.8347),  # Mumbai South / Colaba
            (102, 19.0178, 72.8478),  # Dadar Junction
            (103, 19.0600, 72.8685),  # Bandra Kurla Complex
            (104, 19.1136, 72.8697),  # Andheri East / Airport
            (105, 19.1760, 72.8640),  # Malad / Goregaon
            (106, 19.2288, 72.8541),  # Borivali
            (107, 19.2183, 72.9781),  # Thane West
            (108, 19.0330, 73.0297),  # Navi Mumbai / Vashi
            (109, 18.7546, 73.4062),  # Lonavala Highway Corridor
            (110, 18.5204, 73.8567),  # Pune Central
            (111, 18.6279, 73.8131),  # Pimpri-Chinchwad
            (112, 19.9975, 73.7898),  # Nashik Highway Node
            (113, 19.8762, 75.3433),  # Chhatrapati Sambhajinagar (Aurangabad)
            (114, 21.1458, 79.0882),  # Nagpur Node
        ]
        for nid, lat, lon in nodes:
            self.road_graph.add_node(nid, lat, lon)

        # Corridors / Highways (Western Express, Eastern Express, Mumbai-Pune Expressway, etc.)
        edges = [
            (101, 102, 0.0, 1),
            (102, 103, 0.0, 1),
            (103, 104, 0.0, 1),
            (104, 105, 0.0, 1),
            (105, 106, 0.0, 1),
            (102, 107, 0.0, 1),
            (103, 108, 0.0, 1),
            (107, 108, 0.0, 2),
            (108, 109, 0.0, 1),  # Mumbai-Pune Expressway
            (109, 111, 0.0, 1),
            (111, 110, 0.0, 1),
            (107, 112, 0.0, 1),  # Mumbai-Nashik Corridor
            (112, 113, 0.0, 1),  # Nashik-Sambhajinagar
            (113, 114, 0.0, 1),  # Samruddhi Mahamarg to Nagpur
        ]
        for f, t, d, rt in edges:
            self.road_graph.add_edge(f, t, d, rt, bidirectional=True)

        logger.info("Road graph initialized with %d nodes and %d arterial corridors.", len(nodes), len(edges))

    def get_nearby_facilities_fast(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float = 25.0,
        emergency_only: bool = False,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """O(1) spatial grid query for nearby hospitals."""
        if not self.spatial_index:
            return []
        return self.spatial_index.query_radius(center_lat, center_lon, radius_km, emergency_only, limit)

    def route_to_nearest_hospital(self, user_lat: float, user_lon: float) -> Optional[Dict[str, Any]]:
        """
        Calculates an offline road route from the patient's coordinates to the
        nearest emergency department using the native A* road graph.
        Never fabricates estimated travel times.
        """
        # Find nearest facility with 24/7 ER
        nearby_er = self.get_nearby_facilities_fast(user_lat, user_lon, radius_km=50.0, emergency_only=True, limit=1)
        if not nearby_er:
            nearby_er = self.get_nearby_facilities_fast(user_lat, user_lon, radius_km=100.0, emergency_only=False, limit=1)
        if not nearby_er:
            return None

        target_fac = nearby_er[0]
        target_lat = target_fac["latitude"]
        target_lon = target_fac["longitude"]

        # Snap user and destination to nearest road graph nodes
        start_node = self.road_graph.find_nearest_node(user_lat, user_lon, max_radius_km=100.0)
        target_node = self.road_graph.find_nearest_node(target_lat, target_lon, max_radius_km=100.0)

        if start_node is None or target_node is None:
            # Fall back to direct vector distance
            direct_dist = PythonMapEngine.haversine_km(user_lat, user_lon, target_lat, target_lon)
            return {
                "destination_facility": target_fac,
                "total_distance_km": round(direct_dist, 2),
                "is_direct_vector": True,
                "waypoints": [
                    {"latitude": user_lat, "longitude": user_lon},
                    {"latitude": target_lat, "longitude": target_lon}
                ]
            }

        route = self.road_graph.find_route(start_node, target_node)
        if not route:
            direct_dist = PythonMapEngine.haversine_km(user_lat, user_lon, target_lat, target_lon)
            return {
                "destination_facility": target_fac,
                "total_distance_km": round(direct_dist, 2),
                "is_direct_vector": True,
                "waypoints": [
                    {"latitude": user_lat, "longitude": user_lon},
                    {"latitude": target_lat, "longitude": target_lon}
                ]
            }

        # Prepend actual user position and append actual hospital position
        full_waypoints = [{"latitude": user_lat, "longitude": user_lon}]
        full_waypoints.extend(route["waypoints"])
        full_waypoints.append({"latitude": target_lat, "longitude": target_lon})

        lead_dist = PythonMapEngine.haversine_km(user_lat, user_lon, route["waypoints"][0]["latitude"], route["waypoints"][0]["longitude"])
        tail_dist = PythonMapEngine.haversine_km(route["waypoints"][-1]["latitude"], route["waypoints"][-1]["longitude"], target_lat, target_lon)
        total_road_km = round(route["total_distance_km"] + lead_dist + tail_dist, 2)

        return {
            "destination_facility": target_fac,
            "total_distance_km": total_road_km,
            "node_count": len(full_waypoints),
            "is_direct_vector": False,
            "waypoints": full_waypoints
        }

    def is_in_maharashtra(self, lat: float, lon: float) -> bool:
        """Verifies if coordinates are within the Maharashtra state boundaries."""
        if self.loader.using_native and self.loader.dll:
            try:
                return bool(self.loader.dll.map_package_is_within_maharashtra(lat, lon))
            except Exception:
                pass
        return PythonMapEngine.is_within_maharashtra(lat, lon)

    def lat_lon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int, int]:
        """Calculates Slippy tile coordinate."""
        if self.loader.using_native and self.loader.dll:
            try:
                tc = TileCoord()
                self.loader.dll.geo_lat_lon_to_tile(lat, lon, zoom, ctypes.byref(tc))
                return (tc.zoom, tc.x, tc.y)
            except Exception:
                pass
        return PythonMapEngine.lat_lon_to_tile(lat, lon, zoom)

    def tile_to_lat_lon(self, zoom: int, x: int, y: int) -> Tuple[float, float]:
        """Calculates northwest coordinate for Slippy tile."""
        if self.loader.using_native and self.loader.dll:
            try:
                pt = GeoPoint()
                self.loader.dll.geo_tile_to_lat_lon(zoom, x, y, ctypes.byref(pt))
                return (pt.latitude, pt.longitude)
            except Exception:
                pass
        return PythonMapEngine.tile_to_lat_lon(zoom, x, y)

    def inspect_mbtiles_package(self, mbtiles_path: Path) -> Dict[str, Any]:
        """Reads metadata and verifies integrity of an offline MBTiles package."""
        if not mbtiles_path.exists():
            return {"valid": False, "error": "File does not exist"}

        try:
            conn = sqlite3.connect(str(mbtiles_path))
            cur = conn.cursor()
            cur.execute("SELECT name, value FROM metadata")
            meta = dict(cur.fetchall())

            cur.execute("SELECT COUNT(*) FROM tiles")
            tile_count = cur.fetchone()[0]
            conn.close()

            return {
                "valid": True,
                "format": meta.get("format", "pbf/png"),
                "name": meta.get("name", mbtiles_path.stem),
                "min_zoom": meta.get("minzoom", "0"),
                "max_zoom": meta.get("maxzoom", "14"),
                "bounds": meta.get("bounds", "72.6,15.6,80.9,22.1"),
                "tile_count": tile_count,
                "size_mb": round(mbtiles_path.stat().st_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {"valid": False, "error": f"Corrupt or invalid MBTiles: {e}"}
