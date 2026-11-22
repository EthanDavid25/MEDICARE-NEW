/**
 * MEDICARE Native Geographic Processing & Spatial Indexing Engine (C11)
 *
 * Implements:
 * - WGS84 coordinate validation
 * - Haversine great-circle distance
 * - Equirectangular fast distance
 * - Bounding box arithmetic
 * - Dynamic 2D spatial grid index for ultra-fast nearby facility queries
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "../include/medicare_map_engine.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static inline double deg2rad(double deg) {
    return deg * (M_PI / 180.0);
}

/* -------------------------------------------------------------------------
 * Coordinate Validation & Distance Calculations
 * ------------------------------------------------------------------------- */

bool geo_is_valid_coord(double lat, double lon) {
    if (isnan(lat) || isnan(lon) || isinf(lat) || isinf(lon)) {
        return false;
    }
    return (lat >= -90.0 && lat <= 90.0 && lon >= -180.0 && lon <= 180.0);
}

double geo_haversine_km(double lat1, double lon1, double lat2, double lon2) {
    if (!geo_is_valid_coord(lat1, lon1) || !geo_is_valid_coord(lat2, lon2)) {
        return -1.0;
    }

    double phi1 = deg2rad(lat1);
    double phi2 = deg2rad(lat2);
    double delta_phi = deg2rad(lat2 - lat1);
    double delta_lambda = deg2rad(lon2 - lon1);

    double sin_dphi2 = sin(delta_phi / 2.0);
    double sin_dlam2 = sin(delta_lambda / 2.0);

    double a = (sin_dphi2 * sin_dphi2) +
               (cos(phi1) * cos(phi2) * sin_dlam2 * sin_dlam2);

    if (a < 0.0) a = 0.0;
    if (a > 1.0) a = 1.0;

    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    return EARTH_RADIUS_KM * c;
}

double geo_fast_distance_km(double lat1, double lon1, double lat2, double lon2) {
    double phi1 = deg2rad(lat1);
    double phi2 = deg2rad(lat2);
    double delta_lambda = deg2rad(lon2 - lon1);
    double delta_phi = deg2rad(lat2 - lat1);

    double x = delta_lambda * cos((phi1 + phi2) / 2.0);
    double y = delta_phi;

    return EARTH_RADIUS_KM * sqrt(x * x + y * y);
}

GeoStatus geo_compute_bounding_box(double center_lat, double center_lon, double radius_km, GeoBoundingBox* out_bbox) {
    if (!out_bbox || !geo_is_valid_coord(center_lat, center_lon) || radius_km <= 0.0) {
        return GEO_ERR_INVALID_PARAM;
    }

    /* 1 degree of latitude is approx 111.0 km */
    double lat_delta = radius_km / 111.0;
    /* 1 degree of longitude depends on latitude */
    double cos_lat = cos(deg2rad(center_lat));
    double lon_delta = (cos_lat > 0.0001) ? (radius_km / (111.0 * cos_lat)) : lat_delta;

    out_bbox->min_lat = center_lat - lat_delta;
    out_bbox->max_lat = center_lat + lat_delta;
    out_bbox->min_lon = center_lon - lon_delta;
    out_bbox->max_lon = center_lon + lon_delta;

    if (out_bbox->min_lat < -90.0) out_bbox->min_lat = -90.0;
    if (out_bbox->max_lat > 90.0) out_bbox->max_lat = 90.0;
    if (out_bbox->min_lon < -180.0) out_bbox->min_lon = -180.0;
    if (out_bbox->max_lon > 180.0) out_bbox->max_lon = 180.0;

    return GEO_SUCCESS;
}

bool geo_bbox_contains(const GeoBoundingBox* bbox, double lat, double lon) {
    if (!bbox) return false;
    return (lat >= bbox->min_lat && lat <= bbox->max_lat &&
            lon >= bbox->min_lon && lon <= bbox->max_lon);
}

/* -------------------------------------------------------------------------
 * 2D Spatial Grid Index
 * ------------------------------------------------------------------------- */

typedef struct GridCellNode {
    NativeFacility facility;
    struct GridCellNode* next;
} GridCellNode;

struct SpatialGridIndex {
    double min_lat;
    double min_lon;
    double max_lat;
    double max_lon;
    double cell_size_km;
    double lat_step;
    double lon_step;
    int32_t cols;
    int32_t rows;
    GridCellNode** cells;
};

SpatialGridIndex* spatial_grid_create(double min_lat, double min_lon, double max_lat, double max_lon, double cell_size_km) {
    if (min_lat >= max_lat || min_lon >= max_lon || cell_size_km <= 0.0) {
        return NULL;
    }

    SpatialGridIndex* grid = (SpatialGridIndex*)calloc(1, sizeof(SpatialGridIndex));
    if (!grid) return NULL;

    grid->min_lat = min_lat;
    grid->min_lon = min_lon;
    grid->max_lat = max_lat;
    grid->max_lon = max_lon;
    grid->cell_size_km = cell_size_km;

    grid->lat_step = cell_size_km / 111.0;
    double mid_lat = (min_lat + max_lat) / 2.0;
    double cos_lat = cos(deg2rad(mid_lat));
    grid->lon_step = (cos_lat > 0.0001) ? (cell_size_km / (111.0 * cos_lat)) : grid->lat_step;

    grid->rows = (int32_t)ceil((max_lat - min_lat) / grid->lat_step) + 1;
    grid->cols = (int32_t)ceil((max_lon - min_lon) / grid->lon_step) + 1;

    if (grid->rows <= 0) grid->rows = 1;
    if (grid->cols <= 0) grid->cols = 1;
    if (grid->rows > 2000) grid->rows = 2000;
    if (grid->cols > 2000) grid->cols = 2000;

    size_t total_cells = (size_t)grid->rows * (size_t)grid->cols;
    grid->cells = (GridCellNode**)calloc(total_cells, sizeof(GridCellNode*));
    if (!grid->cells) {
        free(grid);
        return NULL;
    }

    return grid;
}

GeoStatus spatial_grid_insert(SpatialGridIndex* grid, const NativeFacility* facility) {
    if (!grid || !facility) return GEO_ERR_INVALID_PARAM;
    if (!geo_is_valid_coord(facility->latitude, facility->longitude)) return GEO_ERR_INVALID_PARAM;

    int32_t row = (int32_t)floor((facility->latitude - grid->min_lat) / grid->lat_step);
    int32_t col = (int32_t)floor((facility->longitude - grid->min_lon) / grid->lon_step);

    if (row < 0 || row >= grid->rows || col < 0 || col >= grid->cols) {
        return GEO_ERR_OUT_OF_BOUNDS;
    }

    int32_t index = row * grid->cols + col;
    GridCellNode* node = (GridCellNode*)malloc(sizeof(GridCellNode));
    if (!node) return GEO_ERR_ALLOC_FAILED;

    node->facility = *facility;
    node->next = grid->cells[index];
    grid->cells[index] = node;

    return GEO_SUCCESS;
}

static int compare_facility_distance(const void* a, const void* b) {
    const NativeFacility* fa = (const NativeFacility*)a;
    const NativeFacility* fb = (const NativeFacility*)b;
    if (fa->distance_km < fb->distance_km) return -1;
    if (fa->distance_km > fb->distance_km) return 1;
    return 0;
}

int32_t spatial_grid_query_radius(
    const SpatialGridIndex* grid,
    double center_lat,
    double center_lon,
    double radius_km,
    uint8_t emergency_only,
    NativeFacility* out_results,
    int32_t max_results
) {
    if (!grid || !out_results || max_results <= 0 || radius_km <= 0.0) {
        return 0;
    }

    GeoBoundingBox bbox;
    geo_compute_bounding_box(center_lat, center_lon, radius_km, &bbox);

    int32_t min_row = (int32_t)floor((bbox.min_lat - grid->min_lat) / grid->lat_step);
    int32_t max_row = (int32_t)floor((bbox.max_lat - grid->min_lat) / grid->lat_step);
    int32_t min_col = (int32_t)floor((bbox.min_lon - grid->min_lon) / grid->lon_step);
    int32_t max_col = (int32_t)floor((bbox.max_lon - grid->min_lon) / grid->lon_step);

    if (min_row < 0) min_row = 0;
    if (max_row >= grid->rows) max_row = grid->rows - 1;
    if (min_col < 0) min_col = 0;
    if (max_col >= grid->cols) max_col = grid->cols - 1;

    int32_t count = 0;

    for (int32_t r = min_row; r <= max_row; ++r) {
        for (int32_t c = min_col; c <= max_col; ++c) {
            int32_t idx = r * grid->cols + c;
            GridCellNode* curr = grid->cells[idx];
            while (curr) {
                if (!emergency_only || curr->facility.has_emergency) {
                    double dist = geo_haversine_km(center_lat, center_lon, curr->facility.latitude, curr->facility.longitude);
                    if (dist <= radius_km) {
                        if (count < max_results) {
                            out_results[count] = curr->facility;
                            out_results[count].distance_km = (float)dist;
                            count++;
                        }
                    }
                }
                curr = curr->next;
            }
        }
    }

    /* Sort results by distance ascending */
    if (count > 1) {
        qsort(out_results, count, sizeof(NativeFacility), compare_facility_distance);
    }

    return count;
}

void spatial_grid_destroy(SpatialGridIndex* grid) {
    if (!grid) return;
    size_t total_cells = (size_t)grid->rows * (size_t)grid->cols;
    for (size_t i = 0; i < total_cells; ++i) {
        GridCellNode* curr = grid->cells[i];
        while (curr) {
            GridCellNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(grid->cells);
    free(grid);
}
