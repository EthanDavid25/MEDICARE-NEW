/*
 * MEDICARE — data_validator.c
 * Input validation and contradiction detection.
 * Compiled to: medicare_validator.dll
 */
#include <stdio.h>
#include <string.h>
#include "../include/medicare_types.h"

static void add_error(ValidationResult *result, const char *msg) {
    if (!result || result->error_count >= MAX_ERRORS) return;
    snprintf(result->errors[result->error_count], MAX_ERROR_MSG_LEN, "%s", msg);
    result->error_count++;
    result->is_valid = 0;
}

MEDICARE_API void validate_symptom_entry(const SymptomEntry *entry, ValidationResult *result) {
    if (!entry || !result) return;
    result->is_valid = 1;
    result->error_count = 0;
    
    if (entry->code[0] == '\0') add_error(result, "Symptom code must not be empty.");
    if (entry->name[0] == '\0') add_error(result, "Symptom name must not be empty.");
    if (entry->severity < 1 || entry->severity > 10)
        add_error(result, "Severity must be between 1 and 10.");
    if (entry->duration_hours < 0)
        add_error(result, "Duration cannot be negative.");
}

MEDICARE_API void validate_patient_age(int age_years, ValidationResult *result) {
    if (!result) return;
    result->is_valid = 1;
    result->error_count = 0;
    if (age_years < 0 || age_years > 150)
        add_error(result, "Age must be between 0 and 150 years.");
}

MEDICARE_API void check_contradictions(const SymptomEntry *symptoms, int count, ValidationResult *result) {
    if (!symptoms || count <= 0 || !result) return;
    result->is_valid = 1;
    result->error_count = 0;
    for (int i = 0; i < count; i++) {
        if (symptoms[i].is_emergency_flag && symptoms[i].is_worsening == 0) {
            /* Emergency flag but marked as not worsening — flag for review */
            char msg[MAX_ERROR_MSG_LEN];
            snprintf(msg, MAX_ERROR_MSG_LEN,
                "Symptom '%s' is an emergency warning sign but marked as not worsening. Please review.",
                symptoms[i].code);
            add_error(result, msg);
        }
    }
}
