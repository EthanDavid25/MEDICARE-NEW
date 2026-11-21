/*
 * MEDICARE — Medical Symptoms Triage Advisor
 * Shared C type definitions for all native modules.
 */
#ifndef MEDICARE_TYPES_H
#define MEDICARE_TYPES_H

#define MAX_SYMPTOMS 64
#define MAX_RULES 256
#define MAX_SYMPTOM_LEN 128
#define MAX_RULE_CONDITIONS 8
#define MAX_ERROR_MSG_LEN 256
#define MAX_ERRORS 10

/* Urgency categories — lower number = higher urgency */
typedef enum {
    URGENCY_EMERGENCY     = 1,  /* Immediate emergency care required */
    URGENCY_EARLY         = 2,  /* Early medical consultation needed */
    URGENCY_ROUTINE       = 3,  /* Routine healthcare guidance */
    URGENCY_INSUFFICIENT  = 4   /* Insufficient information to assess */
} UrgencyCategory;

/* A single reported symptom */
typedef struct {
    char code[32];
    char name[MAX_SYMPTOM_LEN];
    int  severity;           /* 1–10 */
    int  duration_hours;     /* 0 = unknown */
    int  is_worsening;       /* 1 = yes, 0 = no */
    int  is_emergency_flag;  /* 1 = known emergency warning sign */
} SymptomEntry;

/* A single condition within a triage rule */
typedef struct {
    char symptom_code[32];
    int  min_severity;           /* 0 = no minimum */
    int  requires_worsening;     /* 1 = must be worsening */
    int  is_emergency_override;  /* 1 = auto-escalate to EMERGENCY */
} RuleCondition;

/* A complete triage rule */
typedef struct {
    char         rule_id[32];
    int          urgency_category;
    int          num_conditions;
    RuleCondition conditions[MAX_RULE_CONDITIONS];
    int          is_active;
} TriageRule;

/* Result from input validation */
typedef struct {
    int  is_valid;
    int  error_count;
    char errors[MAX_ERRORS][MAX_ERROR_MSG_LEN];
} ValidationResult;

/* Result from risk calculation */
typedef struct {
    float severity_score;  /* Weighted average severity 1–10 */
    float trend_score;     /* Positive = worsening, negative = improving */
    int   urgency_override;/* 1 = escalate to emergency based on trend */
    char  trend_label[32]; /* "stable", "worsening", "improving", "unknown" */
} RiskResult;

/* DLL export macro */
#ifdef _WIN32
  #define MEDICARE_API __declspec(dllexport)
#else
  #define MEDICARE_API
#endif

#endif /* MEDICARE_TYPES_H */
