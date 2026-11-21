/*
 * MEDICARE — rule_evaluator.c
 * Triage rule evaluation and emergency override logic.
 * Compiled to: medicare_rules.dll
 */
#include <string.h>
#include "../include/medicare_types.h"

MEDICARE_API int check_emergency_override(const SymptomEntry *symptoms, int count) {
    if (!symptoms || count <= 0) return 0;
    for (int i = 0; i < count; i++) {
        if (symptoms[i].is_emergency_flag) return 1;
    }
    return 0;
}

MEDICARE_API int evaluate_single_rule(
    const TriageRule *rule,
    const SymptomEntry *symptoms, int sym_count,
    const int *answers, int answer_count)
{
    if (!rule || !symptoms || sym_count <= 0 || !rule->is_active) return 0;
    
    for (int c = 0; c < rule->num_conditions && c < MAX_RULE_CONDITIONS; c++) {
        const RuleCondition *cond = &rule->conditions[c];
        int cond_met = 0;
        
        for (int s = 0; s < sym_count; s++) {
            if (strncmp(cond->symptom_code, symptoms[s].code, 31) == 0) {
                if (cond->min_severity > 0 && symptoms[s].severity < cond->min_severity) continue;
                if (cond->requires_worsening && !symptoms[s].is_worsening) continue;
                if (cond->is_emergency_override && !symptoms[s].is_emergency_flag) continue;
                cond_met = 1;
                break;
            }
        }
        if (!cond_met) return 0;
    }
    return 1;
}

MEDICARE_API int find_highest_urgency(const int *categories, int count) {
    if (!categories || count <= 0) return URGENCY_INSUFFICIENT;
    int highest = URGENCY_INSUFFICIENT;
    for (int i = 0; i < count; i++) {
        if (categories[i] >= URGENCY_EMERGENCY && categories[i] <= URGENCY_INSUFFICIENT) {
            if (categories[i] < highest) {
                highest = categories[i];
            }
        }
    }
    return highest;
}
