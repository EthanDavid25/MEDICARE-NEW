/*
 * MEDICARE — triage_primitives.c
 * Core urgency resolution primitives.
 * Compiled to: medicare_primitives.dll
 */
#include "../include/medicare_types.h"

MEDICARE_API int apply_emergency_override(int current_category) {
    /* Emergency override always wins — returns URGENCY_EMERGENCY regardless */
    (void)current_category;
    return URGENCY_EMERGENCY;
}

MEDICARE_API int resolve_insufficient_info(int answered, int total_questions, int threshold_pct) {
    if (total_questions <= 0) return URGENCY_INSUFFICIENT;
    int pct = (answered * 100) / total_questions;
    return (pct < threshold_pct) ? URGENCY_INSUFFICIENT : 0;
}

MEDICARE_API int combine_rule_results(const int *triggered_categories, int count) {
    if (!triggered_categories || count <= 0) return URGENCY_INSUFFICIENT;
    int highest = URGENCY_INSUFFICIENT;
    for (int i = 0; i < count; i++) {
        int cat = triggered_categories[i];
        if (cat >= URGENCY_EMERGENCY && cat <= URGENCY_INSUFFICIENT) {
            if (cat < highest) highest = cat;
        }
    }
    return highest;
}
