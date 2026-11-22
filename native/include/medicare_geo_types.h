/**
 * MEDICARE Native Geographic & Offline Map Engine - Type Definitions
 * Standard C11 Header
 *
 * Defines fundamental coordinate, bounding box, spatial grid,
 * road graph, and package verification structures.
 */

#ifndef MEDICARE_GEO_TYPES_H
#define MEDICARE_GEO_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef _WIN32
    #define GEO_EXPORT __declspec(dllexport)
#else
    #define GEO_EXPORT __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Result status codes */
typedef enum {
    GEO_SUCCESS = 0,
    GEO_ERR_INVALID_PARAM = -1,
    GEO_ERR_OUT_OF_BOUNDS = -2,
    GEO_ERR_CORRUPT_PACKAGE = -3,
    GEO_ERR_NO_ROUTE_FOUND = -4,
    GEO_ERR_CACHE_FULL = -5,
    GEO_ERR_ALLOC_FAILED = -6,
    GEO_ERR_TILE_NOT_FOUND = -7
} GeoStatus;

/* Maharashtra regional bounding box (approximate WGS84 coordinates) */
#define MAHARASHTRA_MIN_LAT 15.60
#define MAHARASHTRA_MAX_LAT 22.10
#define MAHARASHTRA_MIN_LON 72.60
#define MAHARASHTRA_MAX_LON 80.90

/* Earth radius constants */
#define EARTH_RADIUS_KM 6371.0088
#define EARTH_RADIUS_METERS 6371008.8

/* Basic 2D Geographic Coordinate (WGS84) */
typedef struct {
    double latitude;
    double longitude;
} GeoPoint;

/* Geographic Bounding Box */
typedef struct {
    double min_lat;
    double min_lon;
    double max_lat;
    double max_lon;
} GeoBoundingBox;

/* Slippy Map Tile Coordinate (Z/X/Y) */
typedef struct {
    int32_t zoom;
    int32_t x;
    int32_t y;
} TileCoord;

/* Healthcare Facility for Native Spatial Processing */
typedef struct {
    int32_t id;
    double latitude;
    double longitude;
    uint8_t has_emergency;   /* 1 = has 24/7 ER, 0 = no ER */
    uint8_t facility_type;   /* 1=Hospital, 2=Clinic, 3=Pharmacy, 4=Diagnostic */
    uint8_t is_verified;     /* 1 = verified local dataset, 0 = sample */
    float distance_km;       /* Populated during spatial queries */
    char name[64];
} NativeFacility;

/* Road Graph Node for Offline Routing */
typedef struct {
    int32_t id;
    double latitude;
    double longitude;
} GraphNode;

/* Road Graph Edge (directional or bidirectional) */
typedef struct {
    int32_t from_node_id;
    int32_t to_node_id;
    double distance_km;
    uint8_t road_type;       /* 1=Highway, 2=Major, 3=Local, 4=Service */
    uint8_t is_bidirectional;
} GraphEdge;

/* Route Search Result */
typedef struct {
    int32_t node_count;
    int32_t max_nodes;
    double total_distance_km;
    GeoPoint* waypoints;     /* Dynamically allocated or buffer */
    GeoStatus status;
} NativeRoute;

#ifdef __cplusplus
}
#endif

#endif /* MEDICARE_GEO_TYPES_H */
