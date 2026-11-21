/*
 * MEDICARE — risk_calculator.c
 * Weighted severity scoring and worsening trend detection.
 * Compiled to: medicare_risk.dll
 */
#include <string.h>
#include <math.h>
#include "../include/medicare_types.h"

MEDICARE_API float calculate_severity_score(const SymptomEntry *symptoms, int count) {
    if (!symptoms || count <= 0) return 0.0f;
    float weighted_sum = 0.0f;
    float weight_total = 0.0f;
    for (int i = 0; i < count; i++) {
        float weight = 1.0f;
        if (symptoms[i].is_emergency_flag) weight = 3.0f;
        if (symptoms[i].is_worsening) weight *= 1.5f;
        weighted_sum += (float)symptoms[i].severity * weight;
        weight_total += weight;
    }
    return (weight_total > 0.0f) ? (weighted_sum / weight_total) : 0.0f;
}

MEDICARE_API float detect_worsening_trend(
    const SymptomEntry *current, int curr_count,
    const SymptomEntry *history, int hist_count)
{
    if (!current || curr_count <= 0) return 0.0f;
    int worsening = 0, improving = 0;
    for (int i = 0; i < curr_count; i++) {
        if (current[i].is_worsening) worsening++;
        else improving++;
    }
    return (float)(worsening - improving);
}

MEDICARE_API void build_risk_result(
    const SymptomEntry *symptoms, int count,
    const SymptomEntry *history, int hist_count,
    RiskResult *result)
{
    if (!result) return;
    result->severity_score = calculate_severity_score(symptoms, count);
    result->trend_score    = detect_worsening_trend(symptoms, count, history, hist_count);
    result->urgency_override = 0;
    
    if (result->trend_score > 0.5f) {
        strncpy(result->trend_label, "worsening", 31);
        if (result->severity_score >= 7.0f) result->urgency_override = 1;
    } else if (result->trend_score < -0.5f) {
        strncpy(result->trend_label, "improving", 31);
    } else if (count > 0) {
        strncpy(result->trend_label, "stable", 31);
    } else {
        strncpy(result->trend_label, "unknown", 31);
    }
    result->trend_label[31] = '\0';
}
