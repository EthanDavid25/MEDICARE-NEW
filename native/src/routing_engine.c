/**
 * MEDICARE Native Offline Routing Engine (C11)
 *
 * Implements:
 * - Dynamic road network graph (nodes, adjacency edge lists)
 * - Spatial nearest-node lookup
 * - A* shortest path search with Haversine distance heuristic
 * - Path reconstruction with real route geometry and distances
 * - Zero fabricated travel times
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "../include/medicare_map_engine.h"

#define INF_DIST 1e12

typedef struct EdgeNode {
    int32_t to_node_idx;
    double distance_km;
    uint8_t road_type;
    struct EdgeNode* next;
} EdgeNode;

typedef struct {
    int32_t user_id;
    double lat;
    double lon;
    EdgeNode* edges;
} InternalNode;

struct RoadGraph {
    InternalNode* nodes;
    int32_t node_count;
    int32_t node_capacity;
};

RoadGraph* road_graph_create(int32_t estimated_nodes, int32_t estimated_edges) {
    if (estimated_nodes <= 0) estimated_nodes = 256;

    RoadGraph* graph = (RoadGraph*)calloc(1, sizeof(RoadGraph));
    if (!graph) return NULL;

    graph->nodes = (InternalNode*)calloc(estimated_nodes, sizeof(InternalNode));
    if (!graph->nodes) {
        free(graph);
        return NULL;
    }

    graph->node_count = 0;
    graph->node_capacity = estimated_nodes;

    return graph;
}

static int32_t find_node_index(const RoadGraph* graph, int32_t user_id) {
    for (int32_t i = 0; i < graph->node_count; ++i) {
        if (graph->nodes[i].user_id == user_id) {
            return i;
        }
    }
    return -1;
}

GeoStatus road_graph_add_node(RoadGraph* graph, int32_t id, double lat, double lon) {
    if (!graph || !geo_is_valid_coord(lat, lon)) return GEO_ERR_INVALID_PARAM;

    /* Check if node already exists */
    if (find_node_index(graph, id) >= 0) {
        return GEO_SUCCESS; /* Idempotent */
    }

    /* Grow capacity if needed */
    if (graph->node_count >= graph->node_capacity) {
        int32_t new_cap = graph->node_capacity * 2;
        InternalNode* new_nodes = (InternalNode*)realloc(graph->nodes, new_cap * sizeof(InternalNode));
        if (!new_nodes) return GEO_ERR_ALLOC_FAILED;
        graph->nodes = new_nodes;
        graph->node_capacity = new_cap;
    }

    int32_t idx = graph->node_count++;
    graph->nodes[idx].user_id = id;
    graph->nodes[idx].lat = lat;
    graph->nodes[idx].lon = lon;
    graph->nodes[idx].edges = NULL;

    return GEO_SUCCESS;
}

static GeoStatus add_half_edge(RoadGraph* graph, int32_t from_idx, int32_t to_idx, double dist_km, uint8_t road_type) {
    EdgeNode* edge = (EdgeNode*)malloc(sizeof(EdgeNode));
    if (!edge) return GEO_ERR_ALLOC_FAILED;

    edge->to_node_idx = to_idx;
    edge->distance_km = dist_km;
    edge->road_type = road_type;
    edge->next = graph->nodes[from_idx].edges;
    graph->nodes[from_idx].edges = edge;

    return GEO_SUCCESS;
}

GeoStatus road_graph_add_edge(RoadGraph* graph, int32_t from_id, int32_t to_id, double distance_km, uint8_t road_type, bool bidirectional) {
    if (!graph || distance_km < 0.0) return GEO_ERR_INVALID_PARAM;

    int32_t from_idx = find_node_index(graph, from_id);
    int32_t to_idx = find_node_index(graph, to_id);

    if (from_idx < 0 || to_idx < 0) return GEO_ERR_INVALID_PARAM;

    /* If distance is 0, compute Haversine automatically between the two nodes */
    if (distance_km == 0.0) {
        distance_km = geo_haversine_km(
            graph->nodes[from_idx].lat, graph->nodes[from_idx].lon,
            graph->nodes[to_idx].lat, graph->nodes[to_idx].lon
        );
    }

    GeoStatus st = add_half_edge(graph, from_idx, to_idx, distance_km, road_type);
    if (st != GEO_SUCCESS) return st;

    if (bidirectional) {
        st = add_half_edge(graph, to_idx, from_idx, distance_km, road_type);
    }

    return st;
}

int32_t road_graph_find_nearest_node(const RoadGraph* graph, double lat, double lon, double max_search_radius_km) {
    if (!graph || graph->node_count == 0 || !geo_is_valid_coord(lat, lon)) {
        return -1;
    }

    int32_t best_user_id = -1;
    double best_dist = max_search_radius_km > 0.0 ? max_search_radius_km : INF_DIST;

    for (int32_t i = 0; i < graph->node_count; ++i) {
        double d = geo_fast_distance_km(lat, lon, graph->nodes[i].lat, graph->nodes[i].lon);
        if (d < best_dist) {
            best_dist = d;
            best_user_id = graph->nodes[i].user_id;
        }
    }

    return best_user_id;
}

/* -------------------------------------------------------------------------
 * A* Routing Implementation
 * ------------------------------------------------------------------------- */

typedef struct {
    int32_t node_idx;
    double f_score;
} PriorityQueueItem;

typedef struct {
    PriorityQueueItem* items;
    int32_t size;
    int32_t capacity;
} PriorityQueue;

static PriorityQueue* pq_create(int32_t cap) {
    PriorityQueue* pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    if (!pq) return NULL;
    pq->items = (PriorityQueueItem*)malloc(cap * sizeof(PriorityQueueItem));
    pq->size = 0;
    pq->capacity = cap;
    return pq;
}

static void pq_push(PriorityQueue* pq, int32_t node_idx, double f_score) {
    if (pq->size >= pq->capacity) {
        pq->capacity *= 2;
        pq->items = (PriorityQueueItem*)realloc(pq->items, pq->capacity * sizeof(PriorityQueueItem));
    }
    int32_t i = pq->size++;
    while (i > 0) {
        int32_t parent = (i - 1) / 2;
        if (pq->items[parent].f_score <= f_score) break;
        pq->items[i] = pq->items[parent];
        i = parent;
    }
    pq->items[i].node_idx = node_idx;
    pq->items[i].f_score = f_score;
}

static int32_t pq_pop(PriorityQueue* pq) {
    if (pq->size == 0) return -1;
    int32_t top = pq->items[0].node_idx;
    PriorityQueueItem last = pq->items[--pq->size];
    if (pq->size > 0) {
        int32_t i = 0;
        while (i * 2 + 1 < pq->size) {
            int32_t left = i * 2 + 1;
            int32_t right = i * 2 + 2;
            int32_t smallest = left;
            if (right < pq->size && pq->items[right].f_score < pq->items[left].f_score) {
                smallest = right;
            }
            if (last.f_score <= pq->items[smallest].f_score) break;
            pq->items[i] = pq->items[smallest];
            i = smallest;
        }
        pq->items[i] = last;
    }
    return top;
}

GeoStatus road_graph_find_route(
    const RoadGraph* graph,
    int32_t start_node_id,
    int32_t target_node_id,
    NativeRoute* out_route
) {
    if (!graph || !out_route) return GEO_ERR_INVALID_PARAM;

    memset(out_route, 0, sizeof(NativeRoute));
    out_route->status = GEO_ERR_NO_ROUTE_FOUND;

    int32_t start_idx = find_node_index(graph, start_node_id);
    int32_t target_idx = find_node_index(graph, target_node_id);

    if (start_idx < 0 || target_idx < 0) return GEO_ERR_INVALID_PARAM;
    if (start_idx == target_idx) {
        out_route->node_count = 1;
        out_route->total_distance_km = 0.0;
        out_route->waypoints = (GeoPoint*)malloc(sizeof(GeoPoint));
        out_route->waypoints[0].latitude = graph->nodes[start_idx].lat;
        out_route->waypoints[0].longitude = graph->nodes[start_idx].lon;
        out_route->status = GEO_SUCCESS;
        return GEO_SUCCESS;
    }

    int32_t N = graph->node_count;
    double* g_score = (double*)malloc(N * sizeof(double));
    int32_t* came_from = (int32_t*)malloc(N * sizeof(int32_t));
    uint8_t* closed_set = (uint8_t*)calloc(N, sizeof(uint8_t));

    for (int32_t i = 0; i < N; ++i) {
        g_score[i] = INF_DIST;
        came_from[i] = -1;
    }

    PriorityQueue* pq = pq_create(N > 64 ? N : 64);
    if (!pq) {
        free(g_score);
        free(came_from);
        free(closed_set);
        return GEO_ERR_ALLOC_FAILED;
    }

    g_score[start_idx] = 0.0;
    double h0 = geo_haversine_km(
        graph->nodes[start_idx].lat, graph->nodes[start_idx].lon,
        graph->nodes[target_idx].lat, graph->nodes[target_idx].lon
    );
    pq_push(pq, start_idx, h0);

    bool found = false;

    while (pq->size > 0) {
        int32_t current = pq_pop(pq);
        if (current == target_idx) {
            found = true;
            break;
        }

        if (closed_set[current]) continue;
        closed_set[current] = 1;

        EdgeNode* edge = graph->nodes[current].edges;
        while (edge) {
            int32_t neighbor = edge->to_node_idx;
            if (!closed_set[neighbor]) {
                double tentative_g = g_score[current] + edge->distance_km;
                if (tentative_g < g_score[neighbor]) {
                    came_from[neighbor] = current;
                    g_score[neighbor] = tentative_g;
                    double h = geo_haversine_km(
                        graph->nodes[neighbor].lat, graph->nodes[neighbor].lon,
                        graph->nodes[target_idx].lat, graph->nodes[target_idx].lon
                    );
                    pq_push(pq, neighbor, tentative_g + h);
                }
            }
            edge = edge->next;
        }
    }

    if (found) {
        /* Count path length */
        int32_t count = 0;
        int32_t curr = target_idx;
        while (curr != -1) {
            count++;
            curr = came_from[curr];
        }

        out_route->waypoints = (GeoPoint*)malloc(count * sizeof(GeoPoint));
        out_route->node_count = count;
        out_route->total_distance_km = g_score[target_idx];
        out_route->status = GEO_SUCCESS;

        /* Reconstruct in forward order */
        curr = target_idx;
        for (int32_t i = count - 1; i >= 0; --i) {
            out_route->waypoints[i].latitude = graph->nodes[curr].lat;
            out_route->waypoints[i].longitude = graph->nodes[curr].lon;
            curr = came_from[curr];
        }
    }

    free(pq->items);
    free(pq);
    free(g_score);
    free(came_from);
    free(closed_set);

    return found ? GEO_SUCCESS : GEO_ERR_NO_ROUTE_FOUND;
}

void road_graph_free_route(NativeRoute* route) {
    if (!route) return;
    if (route->waypoints) {
        free(route->waypoints);
        route->waypoints = NULL;
    }
    route->node_count = 0;
    route->total_distance_km = 0.0;
}

void road_graph_destroy(RoadGraph* graph) {
    if (!graph) return;
    for (int32_t i = 0; i < graph->node_count; ++i) {
        EdgeNode* edge = graph->nodes[i].edges;
        while (edge) {
            EdgeNode* tmp = edge;
            edge = edge->next;
            free(tmp);
        }
    }
    free(graph->nodes);
    free(graph);
}
