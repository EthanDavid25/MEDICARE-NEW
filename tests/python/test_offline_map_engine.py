"""
Unit tests for MEDICARE Offline Map Engine & Geographic Subsystem.
Tests C-compatible Python engine, spatial grid indexing, A* routing,
tile math, boundary validation, and dataset reference integration.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.config import load_config
from app.core.app_controller import AppController
from app.healthcare.native_map_loader import (
    PythonMapEngine,
    PythonTileCache,
    PythonSpatialGridIndex,
    PythonRoadGraph
)

class TestOfflineMapEngine(unittest.TestCase):

    def setUp(self):
        self.config = load_config()
        self.controller = AppController(self.config)
        self.controller.initialize()

    def tearDown(self):
        self.controller.shutdown()

    def test_01_coordinate_validation(self):
        """Verify WGS84 coordinate boundaries and rejection of NaN/inf."""
        self.assertTrue(PythonMapEngine.is_valid_coord(19.0760, 72.8777))
        self.assertTrue(PythonMapEngine.is_valid_coord(-33.8688, 151.2093))
        self.assertFalse(PythonMapEngine.is_valid_coord(91.0, 72.0))
        self.assertFalse(PythonMapEngine.is_valid_coord(-95.0, 0.0))
        self.assertFalse(PythonMapEngine.is_valid_coord(0.0, 185.0))
        self.assertFalse(PythonMapEngine.is_valid_coord(float("nan"), 72.0))
        self.assertFalse(PythonMapEngine.is_valid_coord(19.0, float("inf")))

    def test_02_distance_calculations(self):
        """Verify spherical Haversine and fast equirectangular distance calculations."""
        # Mumbai (18.9220, 72.8347) to Pune (18.5204, 73.8567) is approx 116.5 km
        d_hav = PythonMapEngine.haversine_km(18.9220, 72.8347, 18.5204, 73.8567)
        d_fast = PythonMapEngine.fast_distance_km(18.9220, 72.8347, 18.5204, 73.8567)

        self.assertGreater(d_hav, 115.0)
        self.assertLess(d_hav, 118.0)
        # Fast equirectangular should be within 0.5% for local distances < 200 km
        self.assertAlmostEqual(d_hav, d_fast, delta=0.5)

    def test_03_tile_coordinate_math(self):
        """Verify Slippy map tile coordinate conversion and TMS y-inversion."""
        lat, lon = 19.0760, 72.8777  # Mumbai
        zoom = 12
        z, x, y = PythonMapEngine.lat_lon_to_tile(lat, lon, zoom)
        self.assertEqual(z, 12)
        self.assertEqual(x, 2877)
        self.assertEqual(y, 1826)

        # Invert tile to coordinate — should round-trip close to original
        out_lat, out_lon = PythonMapEngine.tile_to_lat_lon(z, x, y)
        self.assertAlmostEqual(lat, out_lat, delta=0.1)
        self.assertAlmostEqual(lon, out_lon, delta=0.1)

        # TMS inversion: tms_y = (2^zoom - 1) - y
        tms_y = PythonMapEngine.xyz_to_tms_y(zoom, y)
        self.assertEqual(tms_y, (1 << zoom) - 1 - y)

    def test_04_tile_cache_lru(self):
        """Verify LRU in-memory tile cache insertion, retrieval, and eviction."""
        cache = PythonTileCache(max_entries=3, max_bytes=1000)

        cache.put(10, 100, 200, b"tile_data_1")
        cache.put(10, 101, 200, b"tile_data_2")
        cache.put(10, 102, 200, b"tile_data_3")

        self.assertEqual(cache.count(), 3)
        self.assertEqual(cache.get(10, 100, 200), b"tile_data_1")

        # Adding 4th should evict the oldest unaccessed entry (101)
        cache.put(10, 103, 200, b"tile_data_4")
        self.assertEqual(cache.count(), 3)
        self.assertIsNone(cache.get(10, 101, 200))
        self.assertIsNotNone(cache.get(10, 100, 200))
        self.assertIsNotNone(cache.get(10, 103, 200))

    def test_05_spatial_grid_index(self):
        """Verify 2D spatial grid indexing and O(1) nearby facility lookup."""
        grid = PythonSpatialGridIndex(min_lat=15.0, min_lon=72.0, max_lat=23.0, max_lon=81.0, cell_size_km=10.0)

        f1 = {"id": 1, "name": "KEM Hospital Mumbai", "latitude": 19.0028, "longitude": 72.8431, "has_emergency": True}
        f2 = {"id": 2, "name": "Sassoon Hospital Pune", "latitude": 18.5268, "longitude": 73.8739, "has_emergency": True}
        f3 = {"id": 3, "name": "Local Clinic Dadar", "latitude": 19.0178, "longitude": 72.8478, "has_emergency": False}

        grid.insert(f1)
        grid.insert(f2)
        grid.insert(f3)

        # Query 5 km radius around Dadar, Mumbai (19.0178, 72.8478)
        nearby = grid.query_radius(19.0178, 72.8478, radius_km=5.0, emergency_only=False)
        self.assertGreaterEqual(len(nearby), 2)  # Should match KEM and Local Clinic
        # Sassoon (Pune) is ~120 km away, must not match 5 km radius
        matched_ids = [item["id"] for item in nearby]
        self.assertIn(1, matched_ids)
        self.assertIn(3, matched_ids)
        self.assertNotIn(2, matched_ids)

        # Query with emergency_only=True
        nearby_er = grid.query_radius(19.0178, 72.8478, radius_km=5.0, emergency_only=True)
        er_ids = [item["id"] for item in nearby_er]
        self.assertIn(1, er_ids)
        self.assertNotIn(3, er_ids)

    def test_06_offline_road_routing_astar(self):
        """Verify A* search over road network graph without fabricated travel times."""
        graph = PythonRoadGraph()

        # Triangle network: A (0,0) - B (10km) - C (20km); A to C direct is 25km
        graph.add_node(1, 19.00, 72.80)
        graph.add_node(2, 19.05, 72.82)
        graph.add_node(3, 19.10, 72.85)

        graph.add_edge(1, 2, dist_km=6.0, bidirectional=True)
        graph.add_edge(2, 3, dist_km=7.0, bidirectional=True)
        graph.add_edge(1, 3, dist_km=20.0, bidirectional=True)

        route = graph.find_route(1, 3)
        self.assertIsNotNone(route)
        self.assertEqual(route["status"], "SUCCESS")
        # Optimal route should be 1 -> 2 -> 3 = 13.0 km (not the 20 km edge)
        self.assertEqual(route["node_count"], 3)
        self.assertAlmostEqual(route["total_distance_km"], 13.0, delta=0.1)

    def test_07_maharashtra_regional_bounds(self):
        """Verify regional boundary validation for Maharashtra."""
        # Inside Maharashtra: Mumbai, Pune, Nagpur, Nashik
        self.assertTrue(PythonMapEngine.is_within_maharashtra(19.0760, 72.8777))  # Mumbai
        self.assertTrue(PythonMapEngine.is_within_maharashtra(18.5204, 73.8567))  # Pune
        self.assertTrue(PythonMapEngine.is_within_maharashtra(21.1458, 79.0882))  # Nagpur

        # Outside Maharashtra: Delhi, London, Tokyo, New York
        self.assertFalse(PythonMapEngine.is_within_maharashtra(28.6139, 77.2090)) # Delhi
        self.assertFalse(PythonMapEngine.is_within_maharashtra(51.5074, -0.1278)) # London
        self.assertFalse(PythonMapEngine.is_within_maharashtra(40.7128, -74.0060)) # New York

    def test_08_duplicate_facility_detection(self):
        """Verify duplicate facility detection by proximity and name similarity."""
        facilities = [
            {"id": 1, "name": "Lilavati Hospital", "latitude": 19.0515, "longitude": 72.8290},
            {"id": 2, "name": "Lilavati Hospital & Research", "latitude": 19.0516, "longitude": 72.8291}, # Duplicate (15m away)
            {"id": 3, "name": "KEM Hospital", "latitude": 19.0028, "longitude": 72.8431}
        ]
        duplicates = PythonMapEngine.detect_duplicates(facilities, threshold_km=0.050)
        self.assertIn(1, duplicates)  # Index 1 is duplicate of Index 0
        self.assertNotIn(0, duplicates)
        self.assertNotIn(2, duplicates)

    def test_09_offline_map_service_integration(self):
        """Verify OfflineMapService integration with AppController."""
        service = self.controller.offline_map_service
        self.assertIsNotNone(service)

        # Test nearby facility lookup
        nearby = service.get_nearby_facilities_fast(19.0760, 72.8777, radius_km=50.0, limit=5)
        self.assertIsInstance(nearby, list)

        # Test hospital route calculation
        route = service.route_to_nearest_hospital(19.0760, 72.8777)
        if route:
            self.assertIn("total_distance_km", route)
            self.assertIn("waypoints", route)
            self.assertGreater(len(route["waypoints"]), 1)

    def test_10_map_references_dataset_integrity(self):
        """Verify all 8 medical and 9 genuine map references exist in the dataset."""
        refs = self.controller.dataset_loader.get_medical_references()
        self.assertGreaterEqual(len(refs), 17)

        ref_codes = [r.get("ref_code") for r in refs]
        # Clinical references
        self.assertIn("REF_ICD11_CARDIO", ref_codes)
        self.assertIn("REF_ANAPHYLAXIS_EAACI", ref_codes)
        self.assertIn("REF_SEPSIS3_CRITERIA", ref_codes)

        # Map references
        self.assertIn("REF_GEO_OSM", ref_codes)
        self.assertIn("REF_GEO_OSM_COPYRIGHT", ref_codes)
        self.assertIn("REF_GEO_OSM_DOWNLOADING", ref_codes)
        self.assertIn("REF_GEO_MBTILES_SPEC", ref_codes)
        self.assertIn("REF_GEO_KIVY_MAPVIEW", ref_codes)
        self.assertIn("REF_GEO_SQLITE_DOCS", ref_codes)
        self.assertIn("REF_GEO_VALHALLA", ref_codes)
        self.assertIn("REF_GEO_ANDROID_PERMISSIONS", ref_codes)
        self.assertIn("REF_GEO_CPP_REFERENCE", ref_codes)

if __name__ == "__main__":
    unittest.main()
