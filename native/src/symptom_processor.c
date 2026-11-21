/*
 * MEDICARE — symptom_processor.c
 * Symptom text normalization and deduplication.
 * Compiled to: medicare_symptom.dll
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../include/medicare_types.h"

MEDICARE_API void normalize_symptom(const char *input, char *output, int max_len) {
    if (!input || !output || max_len <= 0) return;
    int j = 0;
    int prev_space = 1;
    for (int i = 0; input[i] != '\0' && j < max_len - 1; i++) {
        char c = input[i];
        if (isalpha((unsigned char)c)) {
            output[j++] = (char)tolower((unsigned char)c);
            prev_space = 0;
        } else if (isspace((unsigned char)c) || c == '-' || c == '_') {
            if (!prev_space && j > 0) {
                output[j++] = ' ';
                prev_space = 1;
            }
        }
        /* punctuation and other chars are skipped */
    }
    /* Trim trailing space */
    while (j > 0 && output[j-1] == ' ') j--;
    output[j] = '\0';
}

MEDICARE_API int deduplicate_symptoms(SymptomEntry *entries, int count) {
    if (!entries || count <= 0) return 0;
    int new_count = 0;
    for (int i = 0; i < count; i++) {
        int duplicate = 0;
        for (int j = 0; j < new_count; j++) {
            if (strncmp(entries[i].code, entries[j].code, 31) == 0) {
                duplicate = 1;
                /* Keep the higher severity entry */
                if (entries[i].severity > entries[j].severity) {
                    entries[j] = entries[i];
                }
                break;
            }
        }
        if (!duplicate) {
            entries[new_count++] = entries[i];
        }
    }
    return new_count;
}
