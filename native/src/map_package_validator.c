/**
 * MEDICARE Native Map Package Validator & Duplicate Facility Detector (C11)
 *
 * Implements:
 * - Maharashtra regional boundary checking
 * - Map package header/integrity validation
 * - Spatial duplicate facility detection
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "../include/medicare_map_engine.h"

/* Magic identifier for MEDICARE binary regional map packages */
static const char MEDICARE_MAP_MAGIC[8] = {'M', 'E', 'D', 'M', 'A', 'P', '0', '1'};
static const char SQLITE_HEADER[16] = "SQLite format 3\000";

bool map_package_is_within_maharashtra(double lat, double lon) {
    if (!geo_is_valid_coord(lat, lon)) return false;
    return (lat >= MAHARASHTRA_MIN_LAT && lat <= MAHARASHTRA_MAX_LAT &&
            lon >= MAHARASHTRA_MIN_LON && lon <= MAHARASHTRA_MAX_LON);
}

GeoStatus map_package_validate_header(
    const uint8_t* header_data,
    size_t header_len,
    char* out_region_name,
    int32_t* out_version,
    int32_t* out_min_zoom,
    int32_t* out_max_zoom
) {
    if (!header_data || header_len < 32) {
        return GEO_ERR_INVALID_PARAM;
    }

    /* Check SQLite / MBTiles container header */
    if (header_len >= 16 && memcmp(header_data, SQLITE_HEADER, 16) == 0) {
        if (out_region_name) strcpy(out_region_name, "MBTiles SQLite Container");
        if (out_version) *out_version = 1;
        if (out_min_zoom) *out_min_zoom = 0;
        if (out_max_zoom) *out_max_zoom = 18;
        return GEO_SUCCESS;
    }

    /* Check MEDICARE custom regional map pack magic */
    if (header_len >= 8 && memcmp(header_data, MEDICARE_MAP_MAGIC, 8) == 0) {
        if (out_region_name) {
            strncpy(out_region_name, (const char*)(header_data + 8), 16);
            out_region_name[15] = '\0';
        }
        if (out_version) *out_version = (int32_t)header_data[24];
        if (out_min_zoom) *out_min_zoom = (int32_t)header_data[25];
        if (out_max_zoom) *out_max_zoom = (int32_t)header_data[26];
        return GEO_SUCCESS;
    }

    return GEO_ERR_CORRUPT_PACKAGE;
}

static void normalize_string(const char* in, char* out, size_t max_len) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0' && j < max_len - 1; ++i) {
        if (isalnum((unsigned char)in[i])) {
            out[j++] = (char)tolower((unsigned char)in[i]);
        }
    }
    out[j] = '\0';
}

int32_t map_package_detect_duplicates(
    const NativeFacility* facilities,
    int32_t count,
    double threshold_km,
    uint8_t* out_is_duplicate
) {
    if (!facilities || count <= 1 || !out_is_duplicate) {
        return 0;
    }

    if (threshold_km <= 0.0) threshold_km = 0.050; /* 50 meters default threshold */

    memset(out_is_duplicate, 0, count * sizeof(uint8_t));
    int32_t dup_count = 0;

    for (int32_t i = 0; i < count; ++i) {
        if (out_is_duplicate[i]) continue;

        char norm_a[64];
        normalize_string(facilities[i].name, norm_a, sizeof(norm_a));

        for (int32_t j = i + 1; j < count; ++j) {
            if (out_is_duplicate[j]) continue;

            double dist = geo_fast_distance_km(
                facilities[i].latitude, facilities[i].longitude,
                facilities[j].latitude, facilities[j].longitude
            );

            if (dist <= threshold_km) {
                char norm_b[64];
                normalize_string(facilities[j].name, norm_b, sizeof(norm_b));

                /* If within proximity and names are similar or identical */
                if (strcmp(norm_a, norm_b) == 0 || strstr(norm_a, norm_b) != NULL || strstr(norm_b, norm_a) != NULL) {
                    /* Mark the unverified or later entry as duplicate */
                    out_is_duplicate[j] = 1;
                    dup_count++;
                }
            }
        }
    }

    return dup_count;
}
