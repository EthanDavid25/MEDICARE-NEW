/**
 * MEDICARE Native Map & Geographic Engine - API Header
 * Standard C11
 *
 * Declares public native functions for:
 * 1. Tile coordinate math & LRU tile memory caching
 * 2. High-speed spatial indexing & distance calculations
 * 3. Offline road graph A* routing
 * 4. Regional map package validation & duplicate facility detection
 */

#ifndef MEDICARE_MAP_ENGINE_H
#define MEDICARE_MAP_ENGINE_H

#include "medicare_geo_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* =========================================================================
 * 1. MAP TILE ENGINE
 * ========================================================================= */

/**
 * Converts WGS84 lat/lon to standard Slippy Map tile coordinates at given zoom.
 */
GEO_EXPORT GeoStatus geo_lat_lon_to_tile(double lat, double lon, int32_t zoom, TileCoord* out_tile);

/**
 * Converts Slippy Map tile coordinate to northwest corner WGS84 lat/lon.
 */
GEO_EXPORT GeoStatus geo_tile_to_lat_lon(int32_t zoom, int32_t x, int32_t y, GeoPoint* out_point);

/**
 * Converts XYZ tile Y coordinate to TMS (MBTiles inverted) Y coordinate.
 */
GEO_EXPORT int32_t geo_xyz_to_tms_y(int32_t zoom, int32_t y);

/**
 * Simple thread-safe in-memory LRU tile cache manager.
 */
typedef struct TileCache TileCache;

GEO_EXPORT TileCache* tile_cache_create(size_t max_entries, size_t max_bytes);
GEO_EXPORT void tile_cache_destroy(TileCache* cache);
GEO_EXPORT GeoStatus tile_cache_put(TileCache* cache, int32_t zoom, int32_t x, int32_t y, const uint8_t* data, size_t size);
GEO_EXPORT const uint8_t* tile_cache_get(TileCache* cache, int32_t zoom, int32_t x, int32_t y, size_t* out_size);
GEO_EXPORT void tile_cache_clear(TileCache* cache);
GEO_EXPORT size_t tile_cache_count(const TileCache* cache);

/* =========================================================================
 * 2. GEOGRAPHIC PROCESSING & SPATIAL INDEX ENGINE
 * ========================================================================= */

/**
 * Validates if coordinates are mathematically valid WGS84 coordinates.
 */
GEO_EXPORT bool geo_is_valid_coord(double lat, double lon);

/**
 * Computes exact great-circle distance between two points using Haversine formula.
 * Returns distance in kilometers.
 */
GEO_EXPORT double geo_haversine_km(double lat1, double lon1, double lat2, double lon2);

/**
 * Computes fast flat-earth equirectangular distance approximation (accurate within < 100km).
 * 3-4x faster than Haversine for local spatial clustering.
 */
GEO_EXPORT double geo_fast_distance_km(double lat1, double lon1, double lat2, double lon2);

/**
 * Computes a bounding box around a center point with a given radius in kilometers.
 */
GEO_EXPORT GeoStatus geo_compute_bounding_box(double center_lat, double center_lon, double radius_km, GeoBoundingBox* out_bbox);

/**
 * Checks whether a point falls within a bounding box.
 */
GEO_EXPORT bool geo_bbox_contains(const GeoBoundingBox* bbox, double lat, double lon);

/**
 * Native 2D Spatial Grid Index for rapid O(1) nearby facility lookups.
 */
typedef struct SpatialGridIndex SpatialGridIndex;

GEO_EXPORT SpatialGridIndex* spatial_grid_create(double min_lat, double min_lon, double max_lat, double max_lon, double cell_size_km);
GEO_EXPORT void spatial_grid_destroy(SpatialGridIndex* grid);
GEO_EXPORT GeoStatus spatial_grid_insert(SpatialGridIndex* grid, const NativeFacility* facility);
GEO_EXPORT int32_t spatial_grid_query_radius(
    const SpatialGridIndex* grid,
    double center_lat,
    double center_lon,
    double radius_km,
    uint8_t emergency_only,
    NativeFacility* out_results,
    int32_t max_results
);

/* =========================================================================
 * 3. OFFLINE ROUTING ENGINE (A* Graph Search)
 * ========================================================================= */

typedef struct RoadGraph RoadGraph;

GEO_EXPORT RoadGraph* road_graph_create(int32_t estimated_nodes, int32_t estimated_edges);
GEO_EXPORT void road_graph_destroy(RoadGraph* graph);
GEO_EXPORT GeoStatus road_graph_add_node(RoadGraph* graph, int32_t id, double lat, double lon);
GEO_EXPORT GeoStatus road_graph_add_edge(RoadGraph* graph, int32_t from_id, int32_t to_id, double distance_km, uint8_t road_type, bool bidirectional);
GEO_EXPORT int32_t road_graph_find_nearest_node(const RoadGraph* graph, double lat, double lon, double max_search_radius_km);

/**
 * Finds shortest path using A* search with Haversine distance heuristic.
 * Allocates waypoints array in out_route (caller must free with road_graph_free_route).
 */
GEO_EXPORT GeoStatus road_graph_find_route(
    const RoadGraph* graph,
    int32_t start_node_id,
    int32_t target_node_id,
    NativeRoute* out_route
);
GEO_EXPORT void road_graph_free_route(NativeRoute* route);

/* =========================================================================
 * 4. DATA PROCESSING & PACKAGE VALIDATOR
 * ========================================================================= */

/**
 * Checks if coordinates fall within Maharashtra regional boundaries.
 */
GEO_EXPORT bool map_package_is_within_maharashtra(double lat, double lon);

/**
 * Validates a map package header/metadata buffer.
 */
GEO_EXPORT GeoStatus map_package_validate_header(
    const uint8_t* header_data,
    size_t header_len,
    char* out_region_name,
    int32_t* out_version,
    int32_t* out_min_zoom,
    int32_t* out_max_zoom
);

/**
 * Identifies duplicate facilities in an array based on coordinate proximity (< threshold_km)
 * and optional name matching.
 * Returns count of duplicates marked in is_duplicate array.
 */
GEO_EXPORT int32_t map_package_detect_duplicates(
    const NativeFacility* facilities,
    int32_t count,
    double threshold_km,
    uint8_t* out_is_duplicate
);

#ifdef __cplusplus
}
#endif

#endif /* MEDICARE_MAP_ENGINE_H */
