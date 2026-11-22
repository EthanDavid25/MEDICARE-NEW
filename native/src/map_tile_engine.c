/**
 * MEDICARE Native Map Tile Engine (C11)
 *
 * Implements:
 * - High-speed tile coordinate math (WGS84 lat/lon <-> Slippy tile x/y/z)
 * - MBTiles TMS y-inversion calculation
 * - Dynamic LRU in-memory tile cache with bounded byte budget
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "../include/medicare_map_engine.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Degrees to radians */
static inline double deg2rad(double deg) {
    return deg * (M_PI / 180.0);
}

/* Radians to degrees */
static inline double rad2deg(double rad) {
    return rad * (180.0 / M_PI);
}

/* -------------------------------------------------------------------------
 * Tile Coordinate Calculations
 * ------------------------------------------------------------------------- */

GeoStatus geo_lat_lon_to_tile(double lat, double lon, int32_t zoom, TileCoord* out_tile) {
    if (!out_tile || zoom < 0 || zoom > 22) {
        return GEO_ERR_INVALID_PARAM;
    }
    if (!geo_is_valid_coord(lat, lon)) {
        return GEO_ERR_INVALID_PARAM;
    }

    /* Clamp latitude to Web Mercator limits (-85.05112878 to 85.05112878) */
    if (lat > 85.05112878) lat = 85.05112878;
    if (lat < -85.05112878) lat = -85.05112878;

    double n = (double)(1 << zoom);
    double lat_rad = deg2rad(lat);

    int32_t x = (int32_t)floor((lon + 180.0) / 360.0 * n);
    int32_t y = (int32_t)floor((1.0 - asinh(tan(lat_rad)) / M_PI) / 2.0 * n);

    if (x < 0) x = 0;
    if (x >= (int32_t)n) x = (int32_t)n - 1;
    if (y < 0) y = 0;
    if (y >= (int32_t)n) y = (int32_t)n - 1;

    out_tile->zoom = zoom;
    out_tile->x = x;
    out_tile->y = y;

    return GEO_SUCCESS;
}

GeoStatus geo_tile_to_lat_lon(int32_t zoom, int32_t x, int32_t y, GeoPoint* out_point) {
    if (!out_point || zoom < 0 || zoom > 22) {
        return GEO_ERR_INVALID_PARAM;
    }

    double n = (double)(1 << zoom);
    if (x < 0 || x >= (int32_t)n || y < 0 || y >= (int32_t)n) {
        return GEO_ERR_INVALID_PARAM;
    }

    double lon = ((double)x / n) * 360.0 - 180.0;
    double lat_rad = atan(sinh(M_PI * (1.0 - 2.0 * (double)y / n)));
    double lat = rad2deg(lat_rad);

    out_point->latitude = lat;
    out_point->longitude = lon;

    return GEO_SUCCESS;
}

int32_t geo_xyz_to_tms_y(int32_t zoom, int32_t y) {
    if (zoom < 0 || zoom > 22) return -1;
    int32_t max_tile = (1 << zoom) - 1;
    return max_tile - y;
}

/* -------------------------------------------------------------------------
 * LRU In-Memory Tile Cache
 * ------------------------------------------------------------------------- */

typedef struct CacheNode {
    int32_t zoom;
    int32_t x;
    int32_t y;
    uint8_t* data;
    size_t size;
    struct CacheNode* prev;
    struct CacheNode* next;
    struct CacheNode* hash_next;
} CacheNode;

#define HASH_BUCKETS 1024

struct TileCache {
    size_t max_entries;
    size_t max_bytes;
    size_t current_entries;
    size_t current_bytes;
    CacheNode* head;  /* Most recently used */
    CacheNode* tail;  /* Least recently used */
    CacheNode* buckets[HASH_BUCKETS];
};

static inline uint32_t tile_hash(int32_t zoom, int32_t x, int32_t y) {
    uint32_t h = (uint32_t)(zoom * 73856093 ^ x * 19349663 ^ y * 83492791);
    return h % HASH_BUCKETS;
}

TileCache* tile_cache_create(size_t max_entries, size_t max_bytes) {
    if (max_entries == 0) max_entries = 128;
    if (max_bytes == 0) max_bytes = 16 * 1024 * 1024; /* 16 MB default */

    TileCache* cache = (TileCache*)calloc(1, sizeof(TileCache));
    if (!cache) return NULL;

    cache->max_entries = max_entries;
    cache->max_bytes = max_bytes;
    cache->current_entries = 0;
    cache->current_bytes = 0;
    cache->head = NULL;
    cache->tail = NULL;

    return cache;
}

static void remove_node_from_list(TileCache* cache, CacheNode* node) {
    if (node->prev) node->prev->next = node->next;
    else cache->head = node->next;

    if (node->next) node->next->prev = node->prev;
    else cache->tail = node->prev;

    node->prev = NULL;
    node->next = NULL;
}

static void push_to_front(TileCache* cache, CacheNode* node) {
    node->prev = NULL;
    node->next = cache->head;
    if (cache->head) cache->head->prev = node;
    cache->head = node;
    if (!cache->tail) cache->tail = node;
}

static void evict_oldest(TileCache* cache) {
    if (!cache->tail) return;

    CacheNode* victim = cache->tail;
    remove_node_from_list(cache, victim);

    /* Remove from hash table */
    uint32_t bucket = tile_hash(victim->zoom, victim->x, victim->y);
    CacheNode** curr = &cache->buckets[bucket];
    while (*curr) {
        if (*curr == victim) {
            *curr = victim->hash_next;
            break;
        }
        curr = &((*curr)->hash_next);
    }

    cache->current_entries--;
    cache->current_bytes -= (sizeof(CacheNode) + victim->size);

    free(victim->data);
    free(victim);
}

GeoStatus tile_cache_put(TileCache* cache, int32_t zoom, int32_t x, int32_t y, const uint8_t* data, size_t size) {
    if (!cache || !data || size == 0) return GEO_ERR_INVALID_PARAM;

    /* Make room if exceeding limits */
    while ((cache->current_entries >= cache->max_entries ||
           (cache->current_bytes + size + sizeof(CacheNode)) > cache->max_bytes) &&
           cache->tail != NULL) {
        evict_oldest(cache);
    }

    CacheNode* node = (CacheNode*)malloc(sizeof(CacheNode));
    if (!node) return GEO_ERR_ALLOC_FAILED;

    node->data = (uint8_t*)malloc(size);
    if (!node->data) {
        free(node);
        return GEO_ERR_ALLOC_FAILED;
    }

    memcpy(node->data, data, size);
    node->zoom = zoom;
    node->x = x;
    node->y = y;
    node->size = size;

    /* Insert into hash bucket */
    uint32_t bucket = tile_hash(zoom, x, y);
    node->hash_next = cache->buckets[bucket];
    cache->buckets[bucket] = node;

    /* Insert as MRU */
    push_to_front(cache, node);

    cache->current_entries++;
    cache->current_bytes += (sizeof(CacheNode) + size);

    return GEO_SUCCESS;
}

const uint8_t* tile_cache_get(TileCache* cache, int32_t zoom, int32_t x, int32_t y, size_t* out_size) {
    if (!cache) return NULL;

    uint32_t bucket = tile_hash(zoom, x, y);
    CacheNode* node = cache->buckets[bucket];

    while (node) {
        if (node->zoom == zoom && node->x == x && node->y == y) {
            /* Move to front of LRU queue */
            if (node != cache->head) {
                remove_node_from_list(cache, node);
                push_to_front(cache, node);
            }
            if (out_size) *out_size = node->size;
            return node->data;
        }
        node = node->hash_next;
    }

    return NULL;
}

void tile_cache_clear(TileCache* cache) {
    if (!cache) return;
    while (cache->tail) {
        evict_oldest(cache);
    }
}

size_t tile_cache_count(const TileCache* cache) {
    return cache ? cache->current_entries : 0;
}

void tile_cache_destroy(TileCache* cache) {
    if (!cache) return;
    tile_cache_clear(cache);
    free(cache);
}
