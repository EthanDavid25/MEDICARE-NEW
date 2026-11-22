/**
 * Authoritative Bundled Clinical Datasets for MEDICARE Mobile.
 * Exported directly from MEDICARE clinical datasets.
 * Version: 1.0.0
 */

export const BUNDLED_SYMPTOMS = [
  {
    "code": "SYM_HEADACHE",
    "name": "Headache",
    "aliases": [
      "head pain",
      "cephalalgia",
      "head ache"
    ],
    "body_system": "neurological",
    "description": "Pain or discomfort in the head, scalp, or neck area, ranging from mild to severe.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_HEADACHE_ONSET",
      "QID_HEADACHE_LOCATION",
      "QID_HEADACHE_ASSOCIATED",
      "QID_PAIN_SEVERITY",
      "QID_PAIN_ONSET_SUDDEN"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_MIGRAINE_HISTORY",
      "RF_STRESS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, affecting daily activity",
      "7-9": "Severe, significantly limiting",
      "10": "Worst headache of life \u2014 emergency warning"
    }
  },
  {
    "code": "SYM_SUDDEN_SEVERE_HEADACHE",
    "name": "Sudden Severe Headache (Thunderclap)",
    "aliases": [
      "thunderclap headache",
      "worst headache of life",
      "sudden onset severe headache"
    ],
    "body_system": "neurological",
    "description": "An abrupt, extremely severe headache reaching maximum intensity within seconds to minutes \u2014 sometimes described as the worst headache of one's life.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_HEADACHE_ONSET",
      "QID_PAIN_ONSET_SUDDEN",
      "QID_HEADACHE_ASSOCIATED"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_SMOKING",
      "RF_FAMILY_CARDIAC"
    ],
    "severity_descriptors": {
      "1-3": "Unlikely thunderclap",
      "4-6": "Assess carefully",
      "7-9": "High urgency \u2014 seek evaluation",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_DIZZINESS",
    "name": "Dizziness",
    "aliases": [
      "lightheadedness",
      "vertigo",
      "spinning sensation",
      "wooziness"
    ],
    "body_system": "neurological",
    "description": "A sensation of unsteadiness, lightheadedness, or a spinning feeling (vertigo) that may impair balance.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_DIZZINESS_ONSET",
      "QID_DIZZINESS_TYPE",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_AGE_OVER_65",
      "RF_BLOOD_THINNERS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, brief episodes",
      "4-6": "Moderate, impairs walking",
      "7-9": "Severe, unable to stand",
      "10": "Incapacitating"
    }
  },
  {
    "code": "SYM_CONFUSION",
    "name": "Confusion / Altered Mental Status",
    "aliases": [
      "disorientation",
      "altered consciousness",
      "mental confusion",
      "delirium"
    ],
    "body_system": "neurological",
    "description": "Sudden or gradual inability to think clearly, disorientation to time, place or person, or changes in alertness.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_DIABETES",
      "RF_HISTORY_STROKE",
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Mild forgetfulness",
      "4-6": "Moderate confusion, needs assistance",
      "7-9": "Severely disoriented",
      "10": "Unresponsive \u2014 emergency"
    }
  },
  {
    "code": "SYM_NUMBNESS_TINGLING",
    "name": "Numbness or Tingling",
    "aliases": [
      "pins and needles",
      "paresthesia",
      "sensory loss",
      "numb limb"
    ],
    "body_system": "neurological",
    "description": "Abnormal sensations including numbness, tingling, or a 'pins and needles' feeling in any body part.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_NUMBNESS_LOCATION",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_DIABETES"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_HISTORY_STROKE",
      "RF_BLOOD_THINNERS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, intermittent",
      "4-6": "Moderate, persistent",
      "7-9": "Severe, affects movement",
      "10": "Complete loss of sensation \u2014 seek urgent evaluation"
    }
  },
  {
    "code": "SYM_LIMB_WEAKNESS",
    "name": "Limb Weakness",
    "aliases": [
      "arm weakness",
      "leg weakness",
      "muscle weakness limb",
      "extremity weakness"
    ],
    "body_system": "neurological",
    "description": "Reduced strength or ability to move one or more limbs, which may appear suddenly or develop gradually.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_WEAKNESS_SIDE",
      "QID_PAIN_ONSET_SUDDEN",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HISTORY_STROKE",
      "RF_HYPERTENSION",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, noticeable but functional",
      "4-6": "Moderate, impairs tasks",
      "7-9": "Severe, cannot lift limb",
      "10": "Complete paralysis \u2014 emergency"
    }
  },
  {
    "code": "SYM_VISION_CHANGES",
    "name": "Vision Changes",
    "aliases": [
      "blurred vision",
      "double vision",
      "vision loss",
      "visual disturbance"
    ],
    "body_system": "neurological",
    "description": "Any change in vision including blurring, double vision, partial or total loss, or flashing lights.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_VISION_TYPE",
      "QID_PAIN_ONSET_SUDDEN",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_HISTORY_STROKE",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Mild blur or flickers",
      "4-6": "Significant change, partial loss",
      "7-9": "Severe, markedly impaired",
      "10": "Complete sudden vision loss \u2014 emergency"
    }
  },
  {
    "code": "SYM_FACIAL_DROOPING",
    "name": "Facial Drooping",
    "aliases": [
      "face drooping",
      "drooping face",
      "facial asymmetry",
      "unilateral facial weakness"
    ],
    "body_system": "neurological",
    "description": "Sudden weakness or drooping on one side of the face \u2014 a key warning sign of possible stroke.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_PAIN_ONSET_SUDDEN",
      "QID_STROKE_ARM_WEAKNESS",
      "QID_STROKE_SPEECH"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_HISTORY_STROKE",
      "RF_DIABETES",
      "RF_SMOKING",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Subtle asymmetry",
      "4-6": "Noticeable droop",
      "7-9": "Marked drooping",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_SPEECH_DIFFICULTY",
    "name": "Speech Difficulty",
    "aliases": [
      "slurred speech",
      "aphasia",
      "difficulty speaking",
      "trouble understanding speech"
    ],
    "body_system": "neurological",
    "description": "Sudden difficulty speaking clearly, finding words, or understanding spoken language \u2014 a warning sign of possible stroke.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_PAIN_ONSET_SUDDEN",
      "QID_STROKE_ARM_WEAKNESS",
      "QID_STROKE_FACE_DROOP"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_HISTORY_STROKE",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Slight slurring",
      "4-6": "Noticeable impairment",
      "7-9": "Cannot communicate clearly",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_LOSS_OF_CONSCIOUSNESS",
    "name": "Loss of Consciousness",
    "aliases": [
      "fainting",
      "syncope",
      "passed out",
      "unresponsive",
      "blackout"
    ],
    "body_system": "neurological",
    "description": "A temporary or prolonged loss of awareness and responsiveness. May be brief (fainting) or prolonged (emergency).",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_CONSCIOUSNESS_DURATION",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_HISTORY_SEIZURE",
      "RF_DIABETES",
      "RF_BLOOD_THINNERS"
    ],
    "severity_descriptors": {
      "1-3": "Brief, recovered fully",
      "4-6": "Prolonged, confused on recovery",
      "7-9": "Extended, slow recovery",
      "10": "Still unresponsive \u2014 call 911"
    }
  },
  {
    "code": "SYM_SEIZURE",
    "name": "Seizure",
    "aliases": [
      "convulsion",
      "fit",
      "epileptic episode"
    ],
    "body_system": "neurological",
    "description": "Uncontrolled electrical activity in the brain causing involuntary movements, altered awareness, or stiffening. Emergency if prolonged (>5 minutes) or first-time.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SEIZURE_DURATION",
      "QID_SEIZURE_HISTORY",
      "QID_SYMPTOM_ONSET"
    ],
    "related_risk_factors": [
      "RF_HISTORY_SEIZURE",
      "RF_DIABETES",
      "RF_HISTORY_STROKE"
    ],
    "severity_descriptors": {
      "1-3": "Brief, known epilepsy, recovered",
      "4-6": "Unusual seizure type or duration",
      "7-9": "Prolonged or repeated",
      "10": "Still seizing \u2014 call 911"
    }
  },
  {
    "code": "SYM_CHEST_PAIN",
    "name": "Chest Pain",
    "aliases": [
      "chest discomfort",
      "chest pressure",
      "chest tightness",
      "angina"
    ],
    "body_system": "cardiovascular",
    "description": "Pain, pressure, squeezing, or discomfort in the chest area. Can have many causes ranging from benign to life-threatening.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_CHEST_RADIATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_CHEST_BREATHING",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_HIGH_CHOLESTEROL",
      "RF_SMOKING",
      "RF_OBESITY",
      "RF_FAMILY_CARDIAC"
    ],
    "severity_descriptors": {
      "1-3": "Mild discomfort",
      "4-6": "Moderate, limiting activity",
      "7-9": "Severe, crushing or squeezing",
      "10": "Worst possible \u2014 emergency"
    }
  },
  {
    "code": "SYM_CHEST_PAIN_RADIATING",
    "name": "Chest Pain Radiating to Arm, Jaw, or Shoulder",
    "aliases": [
      "radiating chest pain",
      "arm pain with chest pain",
      "jaw pain with chest pain"
    ],
    "body_system": "cardiovascular",
    "description": "Chest pain that spreads or radiates to the left arm, jaw, neck, or shoulder \u2014 a classic warning sign of a possible cardiac emergency.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_CHEST_BREATHING"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_HIGH_CHOLESTEROL",
      "RF_SMOKING",
      "RF_FAMILY_CARDIAC"
    ],
    "severity_descriptors": {
      "1-3": "Mild, assess carefully",
      "4-6": "Moderate \u2014 urgent evaluation",
      "7-9": "Severe \u2014 emergency",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_CHEST_TIGHTNESS",
    "name": "Chest Tightness",
    "aliases": [
      "tight chest",
      "chest pressure",
      "heaviness in chest"
    ],
    "body_system": "cardiovascular",
    "description": "A sensation of pressure, heaviness, or squeezing in the chest that may be related to cardiac, respiratory, or musculoskeletal causes.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_CHEST_RADIATION",
      "QID_CHEST_BREATHING",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_ASTHMA",
      "RF_SMOKING",
      "RF_FAMILY_CARDIAC"
    ],
    "severity_descriptors": {
      "1-3": "Mild",
      "4-6": "Moderate, noticeable at rest",
      "7-9": "Severe",
      "10": "Emergency \u2014 call 911"
    }
  },
  {
    "code": "SYM_PALPITATIONS",
    "name": "Palpitations",
    "aliases": [
      "heart pounding",
      "irregular heartbeat awareness",
      "racing heart",
      "heart fluttering"
    ],
    "body_system": "cardiovascular",
    "description": "An uncomfortable awareness of the heart beating \u2014 may feel like pounding, fluttering, skipping, or racing.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_PALPITATION_DURATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_STRESS",
      "RF_STIMULANTS"
    ],
    "severity_descriptors": {
      "1-3": "Occasional, brief",
      "4-6": "Frequent, concerning",
      "7-9": "Continuous or with other symptoms",
      "10": "With chest pain/shortness of breath \u2014 emergency"
    }
  },
  {
    "code": "SYM_IRREGULAR_HEARTBEAT",
    "name": "Irregular Heartbeat",
    "aliases": [
      "arrhythmia",
      "skipped beats",
      "uneven pulse",
      "atrial fibrillation feeling"
    ],
    "body_system": "cardiovascular",
    "description": "A sensation that the heart is beating unevenly, skipping beats, or beating too fast or too slow.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_PAIN_SEVERITY",
      "QID_HISTORY_HEART_CONDITION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_AGE_OVER_65",
      "RF_STIMULANTS"
    ],
    "severity_descriptors": {
      "1-3": "Occasional, brief",
      "4-6": "Persistent, notable",
      "7-9": "Continuous with symptoms",
      "10": "With chest pain/syncope \u2014 emergency"
    }
  },
  {
    "code": "SYM_SHORTNESS_OF_BREATH_WITH_CHEST_PAIN",
    "name": "Shortness of Breath with Chest Pain",
    "aliases": [
      "breathlessness with chest pain",
      "dyspnea with chest pain"
    ],
    "body_system": "cardiovascular",
    "description": "The combination of difficulty breathing and chest pain, which significantly raises concern for a cardiac or pulmonary emergency.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_CHEST_RADIATION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_SMOKING",
      "RF_FAMILY_CARDIAC",
      "RF_COPD"
    ],
    "severity_descriptors": {
      "1-3": "Mild",
      "4-6": "Moderate \u2014 urgent evaluation",
      "7-9": "Severe \u2014 emergency",
      "10": "Emergency \u2014 call 911"
    }
  },
  {
    "code": "SYM_ANKLE_SWELLING",
    "name": "Ankle or Leg Swelling",
    "aliases": [
      "oedema",
      "edema",
      "swollen ankles",
      "swollen legs",
      "peripheral oedema"
    ],
    "body_system": "cardiovascular",
    "description": "Swelling of the ankles, feet, or lower legs due to fluid accumulation, which may indicate cardiac, kidney, or venous issues.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SWELLING_BILATERAL",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_HEART_CONDITION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_AGE_OVER_65",
      "RF_OBESITY",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Mild, end of day only",
      "4-6": "Moderate, persistent",
      "7-9": "Severe, pitting oedema",
      "10": "With breathing difficulty \u2014 emergency"
    }
  },
  {
    "code": "SYM_SHORTNESS_OF_BREATH",
    "name": "Shortness of Breath",
    "aliases": [
      "dyspnea",
      "breathlessness",
      "difficulty breathing",
      "can't catch breath"
    ],
    "body_system": "respiratory",
    "description": "An uncomfortable sensation of not getting enough air, ranging from mild exertional breathlessness to severe rest dyspnea.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_BREATHING_AT_REST",
      "QID_CHEST_BREATHING",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_ASTHMA",
      "RF_COPD",
      "RF_SMOKING",
      "RF_HEART_FAILURE"
    ],
    "severity_descriptors": {
      "1-3": "On exertion only",
      "4-6": "At minimal exertion",
      "7-9": "At rest, significant distress",
      "10": "Unable to breathe \u2014 call 911"
    }
  },
  {
    "code": "SYM_COUGH",
    "name": "Cough",
    "aliases": [
      "dry cough",
      "productive cough",
      "persistent cough",
      "hacking cough"
    ],
    "body_system": "respiratory",
    "description": "A reflex action to clear the airways. May be dry or productive, acute or chronic.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_COUGH_TYPE",
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER",
      "QID_MEDICATION_TAKEN"
    ],
    "related_risk_factors": [
      "RF_SMOKING",
      "RF_ASTHMA",
      "RF_COPD"
    ],
    "severity_descriptors": {
      "1-3": "Occasional, mild",
      "4-6": "Frequent, disruptive",
      "7-9": "Severe, persistent",
      "10": "With blood or severe difficulty \u2014 urgent"
    }
  },
  {
    "code": "SYM_WHEEZING",
    "name": "Wheezing",
    "aliases": [
      "whistling breath",
      "wheeze",
      "noisy breathing"
    ],
    "body_system": "respiratory",
    "description": "A high-pitched whistling sound when breathing, usually caused by narrowed or obstructed airways.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_BREATHING_AT_REST",
      "QID_HISTORY_ASTHMA",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_ASTHMA",
      "RF_COPD",
      "RF_SMOKING",
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, on exertion",
      "4-6": "Moderate, at rest",
      "7-9": "Severe, significant distress",
      "10": "Unable to breathe \u2014 call 911"
    }
  },
  {
    "code": "SYM_SEVERE_BREATHING_DIFFICULTY",
    "name": "Severe Difficulty Breathing",
    "aliases": [
      "severe dyspnea",
      "can't breathe",
      "air hunger",
      "respiratory distress"
    ],
    "body_system": "respiratory",
    "description": "Severe inability to breathe adequately, often with visible distress, use of accessory muscles, or inability to speak in full sentences.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_PAIN_SEVERITY"
    ],
    "related_risk_factors": [
      "RF_ASTHMA",
      "RF_COPD",
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Manageable",
      "4-6": "Significant, seek evaluation",
      "7-9": "Severe \u2014 urgent",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_COUGHING_BLOOD",
    "name": "Coughing Up Blood",
    "aliases": [
      "hemoptysis",
      "blood in sputum",
      "bloody cough",
      "coughing blood"
    ],
    "body_system": "respiratory",
    "description": "Coughing up blood or blood-streaked mucus from the respiratory tract. Any amount warrants prompt evaluation.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_BLOOD_AMOUNT",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_SMOKING",
      "RF_COPD",
      "RF_BLOOD_THINNERS"
    ],
    "severity_descriptors": {
      "1-3": "Streaks only, once",
      "4-6": "Repeated, small amounts",
      "7-9": "Significant volume",
      "10": "Large amount \u2014 emergency"
    }
  },
  {
    "code": "SYM_RAPID_BREATHING",
    "name": "Rapid Breathing",
    "aliases": [
      "tachypnea",
      "fast breathing",
      "hyperventilation"
    ],
    "body_system": "respiratory",
    "description": "An abnormally fast breathing rate that may indicate respiratory distress, anxiety, metabolic disturbance, or other conditions.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_ANXIETY",
      "QID_PAIN_SEVERITY"
    ],
    "related_risk_factors": [
      "RF_ASTHMA",
      "RF_COPD",
      "RF_STRESS"
    ],
    "severity_descriptors": {
      "1-3": "Mildly elevated, temporary",
      "4-6": "Noticeable, persistent",
      "7-9": "Severe, with other symptoms",
      "10": "Emergency \u2014 call 911"
    }
  },
  {
    "code": "SYM_NAUSEA",
    "name": "Nausea",
    "aliases": [
      "feeling sick",
      "queasiness",
      "upset stomach",
      "nauseous"
    ],
    "body_system": "gastrointestinal",
    "description": "An unpleasant sensation of unease in the stomach, often accompanied by the urge to vomit.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_NAUSEA_VOMITING",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER",
      "QID_MEDICATION_TAKEN"
    ],
    "related_risk_factors": [
      "RF_PREGNANCY",
      "RF_RECENT_SURGERY",
      "RF_MEDICATIONS_STEROIDS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, limiting",
      "7-9": "Severe, persistent",
      "10": "With blood or severe abdominal pain \u2014 urgent"
    }
  },
  {
    "code": "SYM_VOMITING",
    "name": "Vomiting",
    "aliases": [
      "throwing up",
      "emesis",
      "being sick"
    ],
    "body_system": "gastrointestinal",
    "description": "Forceful expulsion of stomach contents through the mouth. Repeated vomiting can lead to dehydration.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_VOMITING_BLOOD",
      "QID_SYMPTOM_PROGRESSION",
      "QID_DEHYDRATION_SIGNS",
      "QID_MEDICATION_TAKEN"
    ],
    "related_risk_factors": [
      "RF_PREGNANCY",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "1-2 episodes, manageable",
      "4-6": "Repeated, with dehydration risk",
      "7-9": "Persistent, unable to keep fluids down",
      "10": "With blood \u2014 emergency"
    }
  },
  {
    "code": "SYM_ABDOMINAL_PAIN",
    "name": "Abdominal Pain",
    "aliases": [
      "stomach pain",
      "belly pain",
      "stomach ache",
      "abdominal cramps"
    ],
    "body_system": "gastrointestinal",
    "description": "Pain or discomfort in the abdomen, ranging from mild cramping to severe, potentially indicating various conditions.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_ABDOMINAL_LOCATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_ABDOMINAL_RIGID",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_PREGNANCY",
      "RF_RECENT_SURGERY",
      "RF_MEDICATIONS_NSAIDS"
    ],
    "severity_descriptors": {
      "1-3": "Mild cramping",
      "4-6": "Moderate, limiting",
      "7-9": "Severe, constant",
      "10": "Rigid abdomen or severe \u2014 emergency"
    }
  },
  {
    "code": "SYM_DIARRHEA",
    "name": "Diarrhea",
    "aliases": [
      "loose stools",
      "watery stools",
      "frequent bowel movements"
    ],
    "body_system": "gastrointestinal",
    "description": "Loose, watery, or frequent bowel movements. Can lead to dehydration, especially in the vulnerable.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_DEHYDRATION_SIGNS",
      "QID_BLOOD_IN_STOOL",
      "QID_HISTORY_TRAVEL"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_IMMUNOCOMPROMISED",
      "RF_HISTORY_TRAVEL"
    ],
    "severity_descriptors": {
      "1-3": "1-3 loose stools, mild",
      "4-6": "Frequent, with dehydration signs",
      "7-9": "Severe, bloody, unable to maintain fluids",
      "10": "With severe dehydration or blood \u2014 urgent"
    }
  },
  {
    "code": "SYM_CONSTIPATION",
    "name": "Constipation",
    "aliases": [
      "difficulty passing stools",
      "infrequent bowel movements",
      "hard stools"
    ],
    "body_system": "gastrointestinal",
    "description": "Infrequent, difficult, or incomplete passage of hard stools.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_MEDICATION_TAKEN"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_MEDICATIONS_OPIOIDS"
    ],
    "severity_descriptors": {
      "1-3": "Mildly infrequent",
      "4-6": "Several days, discomfort",
      "7-9": "One week+, significant discomfort",
      "10": "With severe pain or vomiting \u2014 urgent"
    }
  },
  {
    "code": "SYM_BLOATING",
    "name": "Bloating",
    "aliases": [
      "abdominal bloating",
      "distension",
      "gassy",
      "feeling bloated"
    ],
    "body_system": "gastrointestinal",
    "description": "A feeling of fullness or swelling in the abdomen, often accompanied by gas.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_DIGESTIVE_CONDITION"
    ],
    "related_risk_factors": [
      "RF_STRESS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, occasional",
      "4-6": "Moderate, frequent",
      "7-9": "Severe, persistent distension",
      "10": "With severe pain \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_HEARTBURN",
    "name": "Heartburn / Acid Reflux",
    "aliases": [
      "acid reflux",
      "GERD",
      "indigestion",
      "burning in chest"
    ],
    "body_system": "gastrointestinal",
    "description": "A burning sensation in the chest or throat caused by stomach acid flowing back into the oesophagus.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_MEDICATION_TAKEN",
      "QID_HEARTBURN_FOOD_RELATED"
    ],
    "related_risk_factors": [
      "RF_OBESITY",
      "RF_STRESS",
      "RF_SMOKING"
    ],
    "severity_descriptors": {
      "1-3": "Occasional, mild",
      "4-6": "Frequent, disruptive",
      "7-9": "Severe or daily",
      "10": "With swallowing difficulty \u2014 seek evaluation"
    }
  },
  {
    "code": "SYM_BLOOD_IN_STOOL",
    "name": "Blood in Stool",
    "aliases": [
      "rectal bleeding",
      "bloody stool",
      "black tarry stool",
      "haematochezia",
      "melaena"
    ],
    "body_system": "gastrointestinal",
    "description": "Visible red blood or dark tarry stools, indicating bleeding somewhere in the gastrointestinal tract.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_BLOOD_COLOR_STOOL",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_AGE_OVER_65",
      "RF_MEDICATIONS_NSAIDS"
    ],
    "severity_descriptors": {
      "1-3": "Small amount, once",
      "4-6": "Repeated",
      "7-9": "Significant amount, dark tarry",
      "10": "Large volume \u2014 emergency"
    }
  },
  {
    "code": "SYM_DIFFICULTY_SWALLOWING",
    "name": "Difficulty Swallowing",
    "aliases": [
      "dysphagia",
      "trouble swallowing",
      "food sticking",
      "painful swallowing"
    ],
    "body_system": "gastrointestinal",
    "description": "A sensation of food or liquid sticking in the throat or oesophagus, or pain when swallowing.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_WEIGHT_LOSS"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_SMOKING"
    ],
    "severity_descriptors": {
      "1-3": "Occasional difficulty",
      "4-6": "With solids regularly",
      "7-9": "With liquids also",
      "10": "Complete obstruction or with allergic reaction \u2014 emergency"
    }
  },
  {
    "code": "SYM_JOINT_PAIN",
    "name": "Joint Pain",
    "aliases": [
      "arthralgia",
      "joint ache",
      "achy joints",
      "joint discomfort"
    ],
    "body_system": "musculoskeletal",
    "description": "Pain, aching, or soreness in one or more joints.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_JOINT_LOCATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_JOINT_SWELLING",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_OBESITY",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, limiting activity",
      "7-9": "Severe, unable to use joint",
      "10": "Joint locked or severely swollen \u2014 urgent"
    }
  },
  {
    "code": "SYM_BACK_PAIN",
    "name": "Back Pain",
    "aliases": [
      "lower back pain",
      "lumbar pain",
      "upper back pain",
      "backache"
    ],
    "body_system": "musculoskeletal",
    "description": "Pain in the upper, middle, or lower back. Very common and usually musculoskeletal, but rarely can indicate serious causes.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_BACK_LOCATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_BACK_RADIATION",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_OBESITY",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Mild",
      "4-6": "Moderate, limiting activity",
      "7-9": "Severe, limits mobility",
      "10": "With bowel/bladder dysfunction \u2014 emergency"
    }
  },
  {
    "code": "SYM_NECK_PAIN",
    "name": "Neck Pain",
    "aliases": [
      "cervical pain",
      "stiff neck",
      "neck ache",
      "cervicalgia"
    ],
    "body_system": "musculoskeletal",
    "description": "Pain or stiffness in the neck area, ranging from muscle tension to conditions requiring urgent evaluation.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_NECK_STIFFNESS_FEVER",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_STRESS",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Mild tension",
      "4-6": "Moderate, limiting movement",
      "7-9": "Severe, can't move neck",
      "10": "Severe neck stiffness with fever and rash \u2014 emergency (possible meningitis)"
    }
  },
  {
    "code": "SYM_MUSCLE_WEAKNESS",
    "name": "General Muscle Weakness",
    "aliases": [
      "generalised weakness",
      "myasthenia",
      "fatigue and weakness",
      "lack of strength"
    ],
    "body_system": "musculoskeletal",
    "description": "Reduced strength or stamina in the muscles throughout the body, not confined to one limb.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_THYROID"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_DIABETES",
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, limiting daily tasks",
      "7-9": "Severe, needs assistance",
      "10": "Sudden onset paralysis \u2014 emergency"
    }
  },
  {
    "code": "SYM_MUSCLE_CRAMPS",
    "name": "Muscle Cramps",
    "aliases": [
      "muscle spasms",
      "cramping",
      "charley horse",
      "muscle spasm"
    ],
    "body_system": "musculoskeletal",
    "description": "Sudden, involuntary contractions of muscles causing pain, often in the legs.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_DEHYDRATION_SIGNS"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Occasional, brief",
      "4-6": "Frequent, disruptive",
      "7-9": "Severe, persistent",
      "10": "With generalised cramping and weakness \u2014 urgent"
    }
  },
  {
    "code": "SYM_JOINT_SWELLING",
    "name": "Joint Swelling",
    "aliases": [
      "swollen joint",
      "inflamed joint",
      "joint oedema"
    ],
    "body_system": "musculoskeletal",
    "description": "Visible or palpable swelling of one or more joints, which may be accompanied by warmth, redness, or pain.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_JOINT_LOCATION",
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_JOINT_REDNESS"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_OBESITY",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Mild, minor swelling",
      "4-6": "Moderate, noticeable",
      "7-9": "Severe, markedly swollen",
      "10": "With severe pain and inability to move \u2014 urgent"
    }
  },
  {
    "code": "SYM_STIFFNESS",
    "name": "Stiffness",
    "aliases": [
      "joint stiffness",
      "morning stiffness",
      "muscle stiffness",
      "rigidity"
    ],
    "body_system": "musculoskeletal",
    "description": "Difficulty or discomfort when moving joints or muscles, especially after rest.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_STIFFNESS_DURATION",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Brief, resolves quickly",
      "4-6": "Lasts over an hour",
      "7-9": "Persistent throughout day",
      "10": "With severe systemic symptoms \u2014 urgent"
    }
  },
  {
    "code": "SYM_RASH",
    "name": "Skin Rash",
    "aliases": [
      "rash",
      "skin eruption",
      "dermatitis",
      "skin redness"
    ],
    "body_system": "dermatological",
    "description": "An area of irritated or swollen skin that may be red, itchy, bumpy, or blistered.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_RASH_LOCATION",
      "QID_SYMPTOM_ONSET",
      "QID_RASH_SPREAD",
      "QID_HISTORY_ALLERGIES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_ALLERGIES",
      "RF_IMMUNOCOMPROMISED",
      "RF_HISTORY_TRAVEL"
    ],
    "severity_descriptors": {
      "1-3": "Small, localised, non-itchy",
      "4-6": "Spreading, itchy",
      "7-9": "Widespread, painful or blistering",
      "10": "With throat swelling or breathing difficulty \u2014 emergency"
    }
  },
  {
    "code": "SYM_ITCHING",
    "name": "Itching",
    "aliases": [
      "pruritus",
      "skin itch",
      "generalised itch"
    ],
    "body_system": "dermatological",
    "description": "An irritating sensation that creates an urge to scratch, localised or generalised.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_RASH_LOCATION",
      "QID_SYMPTOM_ONSET",
      "QID_HISTORY_ALLERGIES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, occasional",
      "4-6": "Moderate, persistent",
      "7-9": "Severe, disrupts sleep",
      "10": "With rash and throat swelling \u2014 emergency"
    }
  },
  {
    "code": "SYM_HIVES",
    "name": "Hives (Urticaria)",
    "aliases": [
      "urticaria",
      "nettle rash",
      "welts",
      "wheals"
    ],
    "body_system": "dermatological",
    "description": "Raised, itchy welts on the skin that can appear suddenly, potentially as part of an allergic reaction.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_HIVES_THROAT",
      "QID_HISTORY_ALLERGIES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Small area, mild",
      "4-6": "Widespread",
      "7-9": "Extensive, with facial swelling",
      "10": "With throat swelling or breathing difficulty \u2014 emergency (anaphylaxis)"
    }
  },
  {
    "code": "SYM_SKIN_DISCOLORATION",
    "name": "Skin Discoloration",
    "aliases": [
      "jaundice",
      "pallor",
      "cyanosis",
      "yellow skin",
      "bluish skin",
      "pale skin"
    ],
    "body_system": "dermatological",
    "description": "Abnormal changes in skin color including yellowing (jaundice), pallor, or bluish tinge (cyanosis).",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_DISCOLORATION_TYPE",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Mild pallor",
      "4-6": "Noticeable yellowing or pallor",
      "7-9": "Marked discolouration",
      "10": "Bluish tinge (cyanosis) \u2014 emergency"
    }
  },
  {
    "code": "SYM_WOUND_NOT_HEALING",
    "name": "Wound Not Healing",
    "aliases": [
      "non-healing wound",
      "chronic wound",
      "wound that won't heal",
      "slow healing"
    ],
    "body_system": "dermatological",
    "description": "A wound, sore, or ulcer that fails to heal within the expected timeframe.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_WOUND_SIGNS_INFECTION",
      "QID_HISTORY_DIABETES"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_IMMUNOCOMPROMISED",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Slow but improving",
      "4-6": "Not improving over weeks",
      "7-9": "Worsening or infected",
      "10": "With spreading redness and systemic symptoms \u2014 urgent"
    }
  },
  {
    "code": "SYM_BRUISING",
    "name": "Unusual Bruising",
    "aliases": [
      "bruising easily",
      "unexplained bruises",
      "contusions",
      "ecchymosis"
    ],
    "body_system": "dermatological",
    "description": "Bruising that occurs easily or without known cause, possibly indicating a bleeding disorder or medication effect.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_BLOOD_THINNERS"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Minor, occasional",
      "4-6": "Frequent, large areas",
      "7-9": "Extensive, unexplained",
      "10": "With active uncontrolled bleeding \u2014 emergency"
    }
  },
  {
    "code": "SYM_FEVER",
    "name": "Fever",
    "aliases": [
      "high temperature",
      "pyrexia",
      "febrile",
      "elevated temperature"
    ],
    "body_system": "general",
    "description": "An elevated body temperature, typically above 38\u00b0C (100.4\u00b0F), usually indicating an immune response to infection or other causes.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_FEVER_TEMPERATURE",
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_FEVER_DURATION",
      "QID_NECK_STIFFNESS_FEVER"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED",
      "RF_AGE_OVER_65",
      "RF_HISTORY_TRAVEL"
    ],
    "severity_descriptors": {
      "1-3": "Low-grade (37.5\u201338\u00b0C)",
      "4-6": "Moderate (38\u201339\u00b0C)",
      "7-9": "High (39\u201340\u00b0C)",
      "10": "Very high >40\u00b0C or with confusion \u2014 urgent"
    }
  },
  {
    "code": "SYM_FATIGUE",
    "name": "Fatigue",
    "aliases": [
      "tiredness",
      "exhaustion",
      "lack of energy",
      "lethargy",
      "chronic tiredness"
    ],
    "body_system": "general",
    "description": "An overwhelming sense of tiredness, lack of energy, or exhaustion not relieved by rest.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_WEIGHT_LOSS",
      "QID_HISTORY_DEPRESSION"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_AGE_OVER_65",
      "RF_HISTORY_DEPRESSION"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, limiting daily activities",
      "7-9": "Severe, bedridden",
      "10": "With other severe symptoms \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_UNEXPLAINED_WEIGHT_LOSS",
    "name": "Unexplained Weight Loss",
    "aliases": [
      "unintentional weight loss",
      "losing weight without trying",
      "unexplained weight change"
    ],
    "body_system": "general",
    "description": "Significant weight loss (typically >5% of body weight) over weeks to months without dieting or increased activity.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_WEIGHT_LOSS_AMOUNT",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_SMOKING",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "1-3 kg, over months",
      "4-6": "4-7 kg over weeks",
      "7-9": "Rapid or large amount",
      "10": "With other alarming symptoms \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_NIGHT_SWEATS",
    "name": "Night Sweats",
    "aliases": [
      "nocturnal sweating",
      "drenching night sweats",
      "sweating at night"
    ],
    "body_system": "general",
    "description": "Excessive sweating during sleep that soaks clothing or bedding, beyond what would be explained by a warm environment.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_WEIGHT_LOSS",
      "QID_HISTORY_FEVER"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED",
      "RF_HISTORY_TRAVEL"
    ],
    "severity_descriptors": {
      "1-3": "Occasional mild sweating",
      "4-6": "Frequent, disruptive",
      "7-9": "Nightly, drenching",
      "10": "With weight loss and fever \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_CHILLS",
    "name": "Chills",
    "aliases": [
      "shivering",
      "rigors",
      "feeling cold with shaking"
    ],
    "body_system": "general",
    "description": "Shivering and feeling cold, often accompanying fever, infection, or other systemic conditions.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_HISTORY_FEVER",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Mild, brief",
      "4-6": "Moderate, with fever",
      "7-9": "Severe rigors",
      "10": "With high fever and altered consciousness \u2014 urgent"
    }
  },
  {
    "code": "SYM_DEHYDRATION",
    "name": "Signs of Dehydration",
    "aliases": [
      "dehydrated",
      "dehydration",
      "not drinking enough",
      "dry mouth thirst"
    ],
    "body_system": "general",
    "description": "Insufficient fluid in the body. Signs include dry mouth, dark urine, decreased urination, dizziness, and confusion.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_DEHYDRATION_SIGNS",
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, dry mouth",
      "4-6": "Moderate, decreased urination",
      "7-9": "Severe, confused or dizzy",
      "10": "Unconscious or unresponsive \u2014 emergency"
    }
  },
  {
    "code": "SYM_FREQUENT_URINATION",
    "name": "Frequent Urination",
    "aliases": [
      "urinary frequency",
      "polyuria",
      "needing to urinate often",
      "frequent trips to bathroom"
    ],
    "body_system": "urological",
    "description": "Needing to urinate more frequently than usual, day or night.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_URINATION_PAIN",
      "QID_HISTORY_DIABETES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_PREGNANCY"
    ],
    "severity_descriptors": {
      "1-3": "Mildly increased",
      "4-6": "Significantly increased, disruptive",
      "7-9": "Very frequent, with other symptoms",
      "10": "With blood in urine and severe pain \u2014 urgent"
    }
  },
  {
    "code": "SYM_PAINFUL_URINATION",
    "name": "Painful Urination",
    "aliases": [
      "dysuria",
      "burning on urination",
      "pain when urinating",
      "stinging when urinating"
    ],
    "body_system": "urological",
    "description": "Pain, burning, or discomfort during urination, often indicating a urinary tract infection or other condition.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_URINATION_BLOOD",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_UTI"
    ],
    "related_risk_factors": [
      "RF_DIABETES",
      "RF_PREGNANCY"
    ],
    "severity_descriptors": {
      "1-3": "Mild burning",
      "4-6": "Moderate, with frequency",
      "7-9": "Severe, with fever or blood",
      "10": "With high fever and back pain \u2014 urgent (possible kidney infection)"
    }
  },
  {
    "code": "SYM_BLOOD_IN_URINE",
    "name": "Blood in Urine",
    "aliases": [
      "haematuria",
      "hematuria",
      "pink or red urine",
      "blood in pee"
    ],
    "body_system": "urological",
    "description": "Visible blood in the urine (pink, red, or brown discolouration) or detected on testing.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_URINATION_PAIN",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_SMOKING",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Faint discolouration, once",
      "4-6": "Repeated, clearly visible",
      "7-9": "Dark red with pain",
      "10": "With severe pain and inability to urinate \u2014 urgent"
    }
  },
  {
    "code": "SYM_REDUCED_URINATION",
    "name": "Reduced or No Urination",
    "aliases": [
      "oliguria",
      "anuria",
      "not urinating",
      "decreased urine output"
    ],
    "body_system": "urological",
    "description": "Significantly decreased or absent urine output, which may indicate kidney problems or severe dehydration.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_DEHYDRATION_SIGNS",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_DIABETES",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Mildly decreased",
      "4-6": "Notably decreased over 24h",
      "7-9": "Very little or none for 12h+",
      "10": "None for 24h+ \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_ANXIETY",
    "name": "Anxiety",
    "aliases": [
      "worry",
      "nervousness",
      "anxious feelings",
      "generalised anxiety"
    ],
    "body_system": "mental_health",
    "description": "Persistent feelings of worry, fear, or unease that may be disproportionate to the situation.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_ANXIETY",
      "QID_HISTORY_MEDICATION_PSYCH"
    ],
    "related_risk_factors": [
      "RF_STRESS",
      "RF_HISTORY_DEPRESSION",
      "RF_STIMULANTS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, impairs daily life",
      "7-9": "Severe, constant distress",
      "10": "With thoughts of self-harm \u2014 seek immediate help"
    }
  },
  {
    "code": "SYM_DEPRESSION_SYMPTOMS",
    "name": "Depression Symptoms",
    "aliases": [
      "low mood",
      "feeling depressed",
      "persistent sadness",
      "loss of interest"
    ],
    "body_system": "mental_health",
    "description": "Persistent low mood, loss of interest in activities, fatigue, or other symptoms of depression lasting more than two weeks.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_DEPRESSION",
      "QID_HISTORY_MEDICATION_PSYCH",
      "QID_SELF_HARM_IDEATION"
    ],
    "related_risk_factors": [
      "RF_STRESS",
      "RF_HISTORY_DEPRESSION"
    ],
    "severity_descriptors": {
      "1-3": "Mild, manageable",
      "4-6": "Moderate, impairs daily life",
      "7-9": "Severe, unable to function",
      "10": "With thoughts of self-harm \u2014 seek immediate help"
    }
  },
  {
    "code": "SYM_PANIC_ATTACKS",
    "name": "Panic Attacks",
    "aliases": [
      "panic attack",
      "panic episode",
      "sudden intense fear",
      "acute anxiety attack"
    ],
    "body_system": "mental_health",
    "description": "Sudden episodes of intense fear or discomfort that peak within minutes, with physical symptoms such as racing heart, sweating, or difficulty breathing.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_PANIC_DURATION",
      "QID_HISTORY_ANXIETY",
      "QID_CHEST_BREATHING"
    ],
    "related_risk_factors": [
      "RF_STRESS",
      "RF_HISTORY_DEPRESSION",
      "RF_STIMULANTS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, brief",
      "4-6": "Moderate, disruptive",
      "7-9": "Severe, frequent",
      "10": "With chest pain \u2014 rule out cardiac cause"
    }
  },
  {
    "code": "SYM_ANAPHYLAXIS",
    "name": "Severe Allergic Reaction / Anaphylaxis",
    "aliases": [
      "anaphylaxis",
      "severe allergy",
      "anaphylactic shock",
      "severe allergic response"
    ],
    "body_system": "emergency",
    "description": "A severe, potentially life-threatening allergic reaction affecting multiple body systems. Signs include throat swelling, difficulty breathing, hives, low blood pressure, and collapse.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_ANAPHYLAXIS_THROAT",
      "QID_HISTORY_ALLERGIES"
    ],
    "related_risk_factors": [
      "RF_ALLERGIES",
      "RF_HISTORY_ANAPHYLAXIS"
    ],
    "severity_descriptors": {
      "1-3": "Unlikely anaphylaxis",
      "4-6": "Possible \u2014 assess urgently",
      "7-9": "Probable \u2014 administer epinephrine if available",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_UNCONTROLLED_BLEEDING",
    "name": "Uncontrolled Bleeding",
    "aliases": [
      "severe bleeding",
      "bleeding that won't stop",
      "haemorrhage",
      "heavy bleeding"
    ],
    "body_system": "emergency",
    "description": "Bleeding that cannot be controlled with direct pressure, or internal bleeding suspected.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_BLEEDING_LOCATION",
      "QID_HISTORY_BLOOD_THINNERS"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_RECENT_SURGERY"
    ],
    "severity_descriptors": {
      "1-3": "Controlled with pressure",
      "4-6": "Difficult to control",
      "7-9": "Cannot control",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_SIGNS_OF_SHOCK",
    "name": "Signs of Shock",
    "aliases": [
      "shock",
      "circulatory shock",
      "pale clammy unconscious",
      "low blood pressure collapse"
    ],
    "body_system": "emergency",
    "description": "A life-threatening condition where the body cannot supply enough blood to vital organs. Signs include pale clammy skin, rapid weak pulse, confusion, and loss of consciousness.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_BLOOD_THINNERS",
      "RF_RECENT_SURGERY",
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Unlikely shock",
      "4-6": "Possible \u2014 assess urgently",
      "7-9": "Probable \u2014 urgent action needed",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_STROKE_SIGNS",
    "name": "Signs of Stroke (FAST)",
    "aliases": [
      "stroke symptoms",
      "FAST stroke",
      "face arm speech time",
      "possible stroke"
    ],
    "body_system": "emergency",
    "description": "Warning signs of stroke using the FAST acronym: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_STROKE_FACE_DROOP",
      "QID_STROKE_ARM_WEAKNESS",
      "QID_STROKE_SPEECH",
      "QID_PAIN_ONSET_SUDDEN"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_HISTORY_STROKE",
      "RF_SMOKING",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "No stroke signs",
      "4-6": "One sign present \u2014 assess urgently",
      "7-9": "Two signs present \u2014 high suspicion",
      "10": "Emergency \u2014 call 911 immediately"
    }
  },
  {
    "code": "SYM_SWEATING",
    "name": "Excessive Sweating",
    "aliases": [
      "diaphoresis",
      "hyperhidrosis",
      "cold sweats",
      "profuse sweating"
    ],
    "body_system": "general",
    "description": "Abnormal or excessive sweating, particularly cold sweats, which may accompany cardiac events, infections, or anxiety.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SWEATING_WITH_CHEST_PAIN",
      "QID_HISTORY_FEVER",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_STRESS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, occasional",
      "4-6": "Frequent",
      "7-9": "Profuse with other symptoms",
      "10": "With chest pain or collapse \u2014 emergency"
    }
  },
  {
    "code": "SYM_LOSS_OF_APPETITE",
    "name": "Loss of Appetite",
    "aliases": [
      "anorexia",
      "not hungry",
      "poor appetite",
      "reduced appetite"
    ],
    "body_system": "general",
    "description": "Reduced desire to eat, which can accompany many conditions including infections, mental health conditions, and chronic disease.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_WEIGHT_LOSS",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_HISTORY_DEPRESSION"
    ],
    "severity_descriptors": {
      "1-3": "Mild, temporary",
      "4-6": "Moderate, over days",
      "7-9": "Severe, prolonged",
      "10": "With significant weight loss \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_SORE_THROAT",
    "name": "Sore Throat",
    "aliases": [
      "throat pain",
      "pharyngitis",
      "throat infection",
      "strep throat"
    ],
    "body_system": "respiratory",
    "description": "Pain, scratchiness, or irritation of the throat, often worsening when swallowing.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER",
      "QID_DIFFICULTY_BREATHING_THROAT"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Mild, occasional",
      "4-6": "Moderate, with fever",
      "7-9": "Severe, difficulty swallowing",
      "10": "With throat swelling or stridor \u2014 emergency"
    }
  },
  {
    "code": "SYM_RUNNY_NOSE",
    "name": "Runny Nose",
    "aliases": [
      "rhinorrhoea",
      "nasal discharge",
      "nasal drip",
      "post-nasal drip"
    ],
    "body_system": "respiratory",
    "description": "Excess nasal mucus discharge, commonly associated with colds, allergies, or sinusitis.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_ALLERGIES"
    ],
    "related_risk_factors": [
      "RF_ALLERGIES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, brief",
      "4-6": "Moderate, persistent",
      "7-9": "Severe, with other symptoms",
      "10": "Unlikely to be emergency"
    }
  },
  {
    "code": "SYM_EAR_PAIN",
    "name": "Ear Pain",
    "aliases": [
      "earache",
      "otalgia",
      "ear infection pain"
    ],
    "body_system": "neurological",
    "description": "Pain in one or both ears, which may be caused by infection, injury, or referred pain from nearby structures.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Mild",
      "4-6": "Moderate, with fever",
      "7-9": "Severe",
      "10": "With high fever and altered hearing \u2014 seek evaluation"
    }
  },
  {
    "code": "SYM_EYE_PAIN",
    "name": "Eye Pain",
    "aliases": [
      "ocular pain",
      "eye ache",
      "painful eye",
      "eye soreness"
    ],
    "body_system": "neurological",
    "description": "Pain in or around one or both eyes, which may accompany redness, swelling, or vision changes.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_VISION_TYPE",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, brief",
      "4-6": "Moderate, with redness",
      "7-9": "Severe",
      "10": "With sudden vision loss \u2014 emergency"
    }
  },
  {
    "code": "SYM_SUDDEN_VISION_LOSS",
    "name": "Sudden Loss of Vision",
    "aliases": [
      "sudden blindness",
      "vision suddenly gone",
      "curtain over vision",
      "sudden visual loss"
    ],
    "body_system": "neurological",
    "description": "Sudden, complete or partial loss of vision in one or both eyes, which is a medical emergency.",
    "is_emergency_warning": true,
    "default_followup_questions": [
      "QID_PAIN_ONSET_SUDDEN",
      "QID_VISION_TYPE"
    ],
    "related_risk_factors": [
      "RF_HYPERTENSION",
      "RF_DIABETES",
      "RF_HISTORY_STROKE",
      "RF_AGE_OVER_65"
    ],
    "severity_descriptors": {
      "1-3": "Blurred",
      "4-6": "Partial loss",
      "7-9": "Significant loss",
      "10": "Complete sudden loss \u2014 emergency"
    }
  },
  {
    "code": "SYM_URINARY_INCONTINENCE",
    "name": "Urinary Incontinence",
    "aliases": [
      "leaking urine",
      "bladder leakage",
      "loss of bladder control"
    ],
    "body_system": "urological",
    "description": "Involuntary leakage of urine.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_UROLOGICAL"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_PREGNANCY"
    ],
    "severity_descriptors": {
      "1-3": "Occasional minor leakage",
      "4-6": "Frequent",
      "7-9": "Complete loss of control",
      "10": "With sudden onset and back pain \u2014 urgent (cauda equina)"
    }
  },
  {
    "code": "SYM_FLANK_PAIN",
    "name": "Flank Pain",
    "aliases": [
      "kidney pain",
      "side pain",
      "loin pain",
      "renal pain"
    ],
    "body_system": "urological",
    "description": "Pain in the side of the torso between the lower ribs and hip, often associated with kidney conditions.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_PAIN_SEVERITY",
      "QID_SYMPTOM_ONSET",
      "QID_URINATION_BLOOD",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_HISTORY_KIDNEY_STONES",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild, dull ache",
      "4-6": "Moderate, with urinary symptoms",
      "7-9": "Severe, colicky pain",
      "10": "Excruciating with urinary symptoms \u2014 urgent"
    }
  },
  {
    "code": "SYM_MOUTH_ULCERS",
    "name": "Mouth Ulcers",
    "aliases": [
      "oral ulcers",
      "canker sores",
      "mouth sores",
      "aphthous ulcers"
    ],
    "body_system": "gastrointestinal",
    "description": "Painful sores inside the mouth on the cheeks, tongue, or gums.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_DIGESTIVE_CONDITION"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED",
      "RF_STRESS"
    ],
    "severity_descriptors": {
      "1-3": "1-2 small sores",
      "4-6": "Multiple, painful",
      "7-9": "Extensive, affecting eating",
      "10": "With systemic symptoms \u2014 seek evaluation"
    }
  },
  {
    "code": "SYM_HAIR_LOSS",
    "name": "Hair Loss",
    "aliases": [
      "alopecia",
      "hair thinning",
      "losing hair",
      "bald patches"
    ],
    "body_system": "dermatological",
    "description": "Loss of hair from the scalp or body, which may be patchy or diffuse.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_THYROID"
    ],
    "related_risk_factors": [
      "RF_STRESS",
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Mild thinning",
      "4-6": "Noticeable patches",
      "7-9": "Extensive loss",
      "10": "Unlikely to be emergency"
    }
  },
  {
    "code": "SYM_TREMORS",
    "name": "Tremors",
    "aliases": [
      "shaking hands",
      "hand tremor",
      "trembling",
      "uncontrollable shaking"
    ],
    "body_system": "neurological",
    "description": "Involuntary, rhythmic muscle contractions causing shaking movements in one or more body parts.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_MEDICATION_PSYCH"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_STIMULANTS"
    ],
    "severity_descriptors": {
      "1-3": "Mild, occasional",
      "4-6": "Moderate, noticeable",
      "7-9": "Severe, affects function",
      "10": "Sudden severe tremor with other symptoms \u2014 urgent"
    }
  },
  {
    "code": "SYM_MEMORY_PROBLEMS",
    "name": "Memory Problems",
    "aliases": [
      "forgetfulness",
      "memory loss",
      "cognitive decline",
      "can't remember"
    ],
    "body_system": "neurological",
    "description": "Difficulty remembering recent events, following instructions, or other memory-related concerns.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_AGE_OVER_65"
    ],
    "related_risk_factors": [
      "RF_AGE_OVER_65",
      "RF_HYPERTENSION",
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Occasional forgetfulness",
      "4-6": "Noticeable impact on daily life",
      "7-9": "Significant, concerning",
      "10": "Sudden severe memory loss \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_INCREASED_THIRST",
    "name": "Increased Thirst",
    "aliases": [
      "polydipsia",
      "excessive thirst",
      "always thirsty",
      "can't quench thirst"
    ],
    "body_system": "general",
    "description": "Feeling unusually thirsty despite adequate fluid intake, which can be associated with diabetes, dehydration, or other conditions.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_HISTORY_DIABETES",
      "QID_FREQUENT_URINATION"
    ],
    "related_risk_factors": [
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mildly increased",
      "4-6": "Notably persistent",
      "7-9": "Severe, with frequent urination",
      "10": "With confusion \u2014 urgent evaluation"
    }
  },
  {
    "code": "SYM_SWOLLEN_LYMPH_NODES",
    "name": "Swollen Lymph Nodes",
    "aliases": [
      "lymphadenopathy",
      "swollen glands",
      "lumps in neck armpits groin"
    ],
    "body_system": "general",
    "description": "Enlarged lymph nodes, often felt as lumps in the neck, armpits, or groin, usually indicating immune system activity.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_HISTORY_FEVER",
      "QID_WEIGHT_LOSS"
    ],
    "related_risk_factors": [
      "RF_IMMUNOCOMPROMISED"
    ],
    "severity_descriptors": {
      "1-3": "Small, tender, with infection",
      "4-6": "Enlarged, without clear cause",
      "7-9": "Multiple, persistent",
      "10": "With fever and night sweats \u2014 seek evaluation"
    }
  },
  {
    "code": "SYM_HIGH_BLOOD_SUGAR_SIGNS",
    "name": "Signs of High Blood Sugar",
    "aliases": [
      "hyperglycaemia signs",
      "diabetic symptoms",
      "high glucose signs"
    ],
    "body_system": "general",
    "description": "Signs that blood sugar may be elevated, including increased thirst, frequent urination, blurred vision, and fatigue.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_HISTORY_DIABETES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild",
      "4-6": "Moderate",
      "7-9": "Severe, with confusion or vomiting",
      "10": "With altered consciousness \u2014 emergency"
    }
  },
  {
    "code": "SYM_LOW_BLOOD_SUGAR_SIGNS",
    "name": "Signs of Low Blood Sugar",
    "aliases": [
      "hypoglycaemia signs",
      "low glucose",
      "sugar crash symptoms"
    ],
    "body_system": "general",
    "description": "Signs that blood sugar may be low, including shakiness, sweating, confusion, and in severe cases, loss of consciousness.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_HISTORY_DIABETES",
      "QID_SYMPTOM_PROGRESSION"
    ],
    "related_risk_factors": [
      "RF_DIABETES"
    ],
    "severity_descriptors": {
      "1-3": "Mild shaking, sweating",
      "4-6": "Confusion, difficulty concentrating",
      "7-9": "Severe, can't self-treat",
      "10": "Loss of consciousness \u2014 emergency"
    }
  },
  {
    "code": "SYM_PREGNANCY_CONCERNS",
    "name": "Pregnancy-Related Concerns",
    "aliases": [
      "pregnancy symptoms",
      "prenatal concerns",
      "obstetric symptoms"
    ],
    "body_system": "general",
    "description": "Symptoms of concern during pregnancy such as severe abdominal pain, heavy bleeding, reduced fetal movement, or severe headache.",
    "is_emergency_warning": false,
    "default_followup_questions": [
      "QID_SYMPTOM_ONSET",
      "QID_SYMPTOM_PROGRESSION",
      "QID_PREGNANCY_STATUS"
    ],
    "related_risk_factors": [
      "RF_PREGNANCY"
    ],
    "severity_descriptors": {
      "1-3": "Mild, common in pregnancy",
      "4-6": "Concerning, seek advice",
      "7-9": "Serious \u2014 urgent evaluation",
      "10": "Severe bleeding or no fetal movement \u2014 emergency"
    }
  }
];

export const BUNDLED_QUESTIONS = [
  {
    "question_id": "QID_CHEST_RADIATION",
    "symptom_codes": [
      "SYM_CHEST_PAIN",
      "SYM_CHEST_TIGHTNESS"
    ],
    "symptom_categories": [
      "chest",
      "cardiovascular"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Does chest pain spread to arm?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, spreads to arm or jaw",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, stays in chest",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_CHEST_ASSOCIATED_DYSPNEA",
    "symptom_codes": [
      "SYM_CHEST_PAIN",
      "SYM_CHEST_TIGHTNESS",
      "SYM_PALPITATIONS"
    ],
    "symptom_categories": [
      "chest",
      "cardiovascular"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Any shortness of breath or sweating?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, sweating or breathless",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No other symptoms",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_CHEST_WORSENING_RAPID",
    "symptom_codes": [
      "SYM_CHEST_PAIN",
      "SYM_CHEST_TIGHTNESS"
    ],
    "symptom_categories": [
      "chest"
    ],
    "applicable_progression": [
      "worsening"
    ],
    "is_emergency_safety_check": true,
    "category": "progression_worsening",
    "question_text": "Is chest pain worsening at rest?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, worsening at rest",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, only with physical effort",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_CHEST_UNCHANGED_DURATION",
    "symptom_codes": [
      "SYM_CHEST_PAIN",
      "SYM_CHEST_TIGHTNESS"
    ],
    "symptom_categories": [
      "chest"
    ],
    "applicable_progression": [
      "unchanged"
    ],
    "is_emergency_safety_check": false,
    "category": "persistence",
    "question_text": "How long has chest pain lasted?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "CONSTANT_HOURS",
        "text": "Constant for over 30 minutes",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "INTERMITTENT_DAYS",
        "text": "Comes and goes over days",
        "urgency_weight": 1,
        "triggers_emergency": false
      },
      {
        "code": "POSITIONAL",
        "text": "Changes with posture or breathing",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_CHEST_IMPROVING_CONFIRM",
    "symptom_codes": [
      "SYM_CHEST_PAIN",
      "SYM_CHEST_TIGHTNESS"
    ],
    "symptom_categories": [
      "chest"
    ],
    "applicable_progression": [
      "improving"
    ],
    "is_emergency_safety_check": false,
    "category": "improvement_check",
    "question_text": "Is chest pain steadily improving?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "CONSISTENT_RESOLVING",
        "text": "Yes, steadily resolving",
        "urgency_weight": 0,
        "triggers_emergency": false
      },
      {
        "code": "FLUCTUATING",
        "text": "No, returns repeatedly",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_PAIN_ONSET_SUDDEN",
    "symptom_codes": [
      "SYM_HEADACHE",
      "SYM_SUDDEN_SEVERE_HEADACHE",
      "SYM_CHEST_PAIN",
      "SYM_ABDOMINAL_PAIN"
    ],
    "symptom_categories": [
      "headache",
      "chest",
      "abdominal"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Did severe pain start suddenly?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, sudden peak in seconds",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, started gradually",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_HEADACHE_STIFF_NECK",
    "symptom_codes": [
      "SYM_HEADACHE",
      "SYM_FEVER"
    ],
    "symptom_categories": [
      "headache",
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Can your chin touch your chest?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "NO",
        "text": "No, neck is too stiff",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "YES",
        "text": "Yes, neck bends freely",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_HEADACHE_WORSENING_SIGNS",
    "symptom_codes": [
      "SYM_HEADACHE"
    ],
    "symptom_categories": [
      "headache"
    ],
    "applicable_progression": [
      "worsening"
    ],
    "is_emergency_safety_check": true,
    "category": "progression_worsening",
    "question_text": "Any confusion, vomiting, or vision loss?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, confusion, vomiting or blackout",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No confusion or vomiting",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_HEADACHE_UNCHANGED_NATURE",
    "symptom_codes": [
      "SYM_HEADACHE"
    ],
    "symptom_categories": [
      "headache"
    ],
    "applicable_progression": [
      "unchanged"
    ],
    "is_emergency_safety_check": false,
    "category": "character",
    "question_text": "Is this like past headaches?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "SIMILAR_NORMAL",
        "text": "Yes, familiar usual headache",
        "urgency_weight": 0,
        "triggers_emergency": false
      },
      {
        "code": "NOVEL_DIFFERENT",
        "text": "No, feels completely new",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_HEADACHE_VISION",
    "symptom_codes": [
      "SYM_HEADACHE",
      "SYM_DIZZINESS"
    ],
    "symptom_categories": [
      "headache",
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "neurological",
    "question_text": "Are you having vision changes?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, blurry or double vision",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "No vision problems",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": false,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_STROKE_FAST_FACE",
    "symptom_codes": [
      "SYM_CONFUSION",
      "SYM_DIZZINESS",
      "SYM_NUMBNESS",
      "SYM_WEAKNESS_LIMB"
    ],
    "symptom_categories": [
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Is one side of face drooping?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, face or smile droops",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No facial drooping",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_STROKE_FAST_ARM",
    "symptom_codes": [
      "SYM_CONFUSION",
      "SYM_DIZZINESS",
      "SYM_NUMBNESS",
      "SYM_WEAKNESS_LIMB"
    ],
    "symptom_categories": [
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Does one arm drift downwards?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, one arm is weak",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No weakness in either arm",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_STROKE_FAST_SPEECH",
    "symptom_codes": [
      "SYM_CONFUSION",
      "SYM_HEADACHE",
      "SYM_DIZZINESS"
    ],
    "symptom_categories": [
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Is speech slurred or difficult?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, speech is slurred",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, speaking normally",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_RESP_SEVERITY",
    "symptom_codes": [
      "SYM_SHORTNESS_OF_BREATH",
      "SYM_COUGH",
      "SYM_WHEEZING",
      "SYM_DIFFICULTY_BREATHING"
    ],
    "symptom_categories": [
      "respiratory"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Can you speak full sentences?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "SEVERE",
        "text": "No, only single words",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "MODERATE",
        "text": "Short phrases with pauses",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "MILD",
        "text": "Yes, full sentences easily",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_RESP_STRIDOR_LIPS",
    "symptom_codes": [
      "SYM_SHORTNESS_OF_BREATH",
      "SYM_ALLERGIC_REACTION"
    ],
    "symptom_categories": [
      "respiratory"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Any lip swelling or stridor sound?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, lip swelling or stridor",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No swelling or noisy breathing",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_RESP_WORSENING_SPEED",
    "symptom_codes": [
      "SYM_SHORTNESS_OF_BREATH",
      "SYM_WHEEZING"
    ],
    "symptom_categories": [
      "respiratory"
    ],
    "applicable_progression": [
      "worsening"
    ],
    "is_emergency_safety_check": true,
    "category": "progression_worsening",
    "question_text": "Did breathlessness start within an hour?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, sudden onset within hour",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, gradual over days",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_FEVER_TEMP",
    "symptom_codes": [
      "SYM_FEVER",
      "SYM_CHILLS"
    ],
    "symptom_categories": [
      "fever"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "fever",
    "question_text": "How high is your fever?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "HIGH_GRADE",
        "text": "High: Above 102\u00b0F (38.9\u00b0C)",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "MODERATE",
        "text": "Moderate: 100\u00b0F to 102\u00b0F",
        "urgency_weight": 1,
        "triggers_emergency": false
      },
      {
        "code": "MILD_OR_UNMEASURED",
        "text": "Mild or unmeasured",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_FEVER_WORSENING_DAYS",
    "symptom_codes": [
      "SYM_FEVER"
    ],
    "symptom_categories": [
      "fever"
    ],
    "applicable_progression": [
      "worsening"
    ],
    "is_emergency_safety_check": false,
    "category": "progression_worsening",
    "question_text": "How many days of fever?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "OVER_3_DAYS",
        "text": "More than 3 days",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "1_TO_2_DAYS",
        "text": "Past 1 to 2 days",
        "urgency_weight": 1,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_FEVER_IMMUNO_RISK",
    "symptom_codes": [
      "SYM_FEVER",
      "SYM_FATIGUE"
    ],
    "symptom_categories": [
      "fever"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "risk_factor",
    "question_text": "Are you taking immunosuppressive medicine?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, chemotherapy or immunosuppressants",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "No immune suppression",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": false,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_ABD_RIGIDITY",
    "symptom_codes": [
      "SYM_ABDOMINAL_PAIN"
    ],
    "symptom_categories": [
      "abdominal"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Is your belly hard or rigid?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, hard like a board",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, belly feels soft",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_BLEEDING_SIGNS",
    "symptom_codes": [
      "SYM_NAUSEA_VOMITING",
      "SYM_ABDOMINAL_PAIN",
      "SYM_DIARRHEA"
    ],
    "symptom_categories": [
      "digestive",
      "abdominal"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Any vomiting blood or black stool?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, blood or black stool",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No blood seen",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_DIGEST_DEHYDRATION",
    "symptom_codes": [
      "SYM_NAUSEA_VOMITING",
      "SYM_DIARRHEA"
    ],
    "symptom_categories": [
      "digestive"
    ],
    "applicable_progression": [
      "worsening",
      "unchanged"
    ],
    "is_emergency_safety_check": false,
    "category": "hydration",
    "question_text": "Can you keep fluids down?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "No, unable to keep fluids",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "Yes, drinking normally",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_DIZZINESS_SYNCOPE",
    "symptom_codes": [
      "SYM_DIZZINESS",
      "SYM_PALPITATIONS"
    ],
    "symptom_categories": [
      "dizziness",
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": true,
    "category": "emergency_warning",
    "question_text": "Did you faint or collapse?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, blacked out or fainted",
        "urgency_weight": 3,
        "triggers_emergency": true
      },
      {
        "code": "NO",
        "text": "No, only felt dizzy",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": true
  },
  {
    "question_id": "QID_MSK_DEFORMITY_WEIGHT",
    "symptom_codes": [
      "SYM_JOINT_PAIN",
      "SYM_BACK_PAIN",
      "SYM_NECK_PAIN"
    ],
    "symptom_categories": [
      "musculoskeletal"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "function",
    "question_text": "Can you bear weight on limb?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "No, cannot bear any weight",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "Yes, can bear partial weight",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_GENERAL_IMPROVEMENT_NEW_SIGNS",
    "symptom_codes": [
      "ALL"
    ],
    "symptom_categories": [
      "ALL"
    ],
    "applicable_progression": [
      "improving"
    ],
    "is_emergency_safety_check": false,
    "category": "improvement_check",
    "question_text": "Any new symptoms appearing?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "NEW_SYMPTOMS_PRESENT",
        "text": "Yes, new symptoms started",
        "urgency_weight": 1,
        "triggers_emergency": false
      },
      {
        "code": "NO_NEW_SYMPTOMS",
        "text": "No, feeling steadily better",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": true,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_CALF_SWELLING",
    "symptom_codes": [
      "SYM_LEG_PAIN",
      "SYM_SWELLING"
    ],
    "symptom_categories": [
      "musculoskeletal",
      "cardiovascular"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "risk_factor",
    "question_text": "Is one calf swollen and warm?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, calf is swollen or red",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "No calf swelling",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": false,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_PREGNANCY_STATUS",
    "symptom_codes": [
      "SYM_ABDOMINAL_PAIN",
      "SYM_PELVIC_PAIN"
    ],
    "symptom_categories": [
      "abdominal"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "risk_factor",
    "question_text": "Could you currently be pregnant?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "PREGNANT",
        "text": "Yes or possibly pregnant",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NOT_PREGNANT",
        "text": "No, definitely not pregnant",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": false,
    "triggers_emergency_check": false
  },
  {
    "question_id": "QID_TRAUMA_HEAD",
    "symptom_codes": [
      "SYM_HEADACHE",
      "SYM_DIZZINESS",
      "SYM_CONFUSION"
    ],
    "symptom_categories": [
      "headache",
      "neurological"
    ],
    "applicable_progression": [
      "ALL"
    ],
    "is_emergency_safety_check": false,
    "category": "trauma",
    "question_text": "Did you suffer a head injury?",
    "question_type": "single_choice",
    "options": [
      {
        "code": "YES",
        "text": "Yes, recent blow to head",
        "urgency_weight": 2,
        "triggers_emergency": false
      },
      {
        "code": "NO",
        "text": "No head injury",
        "urgency_weight": 0,
        "triggers_emergency": false
      }
    ],
    "is_required": false,
    "triggers_emergency_check": false
  }
];

export const BUNDLED_RULES = [
  {
    "rule_id": "RULE_EMERG_CHEST_RAD",
    "version": "1.0.0",
    "description": "Chest pain with radiation to arm, jaw, neck, or back",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_CHEST_PAIN",
        "SYM_CHEST_TIGHTNESS"
      ],
      "followup_answers": {
        "QID_CHEST_RADIATION": "YES"
      },
      "min_severity": 4
    },
    "explanation": "Reported chest pain radiating to the arm, jaw, or neck is a classic clinical indicator of possible acute coronary ischemia or aortic syndrome. Emergency intervention is mandatory.",
    "recommended_action": "Call emergency medical services (911 / 112 / 999) immediately. Do not drive yourself. Rest in a comfortable seated position.",
    "clinical_notes": "Immediate 12-lead ECG and cardiac biomarker evaluation needed."
  },
  {
    "rule_id": "RULE_EMERG_STROKE_FAST",
    "version": "1.0.0",
    "description": "Acute focal neurological deficit (Facial droop, arm drift, or speech disturbance)",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "any_followup_answers": {
        "QID_STROKE_FAST_FACE": "YES",
        "QID_STROKE_FAST_ARM": "YES",
        "QID_STROKE_FAST_SPEECH": "YES"
      }
    },
    "explanation": "Sudden onset of facial weakness, unilateral limb paresis, or aphasia/dysarthria indicates acute focal cerebral ischemia or intracranial hemorrhage.",
    "recommended_action": "Activate emergency stroke protocol immediately. Note the exact time the patient was last seen normal. Do NOT administer aspirin until head CT excludes hemorrhage.",
    "clinical_notes": "Time-sensitive window for intravenous thrombolysis or endovascular thrombectomy."
  },
  {
    "rule_id": "RULE_EMERG_SEVERE_RESP_DISTRESS",
    "version": "1.0.0",
    "description": "Severe shortness of breath with inability to speak full sentences",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_SHORTNESS_OF_BREATH"
      ],
      "followup_answers": {
        "QID_RESP_SEVERITY": "SEVERE"
      }
    },
    "explanation": "Inability to formulate complete phrases due to dyspnea signifies impending ventilatory compromise or critical gas exchange impairment.",
    "recommended_action": "Seek immediate emergency department care. Sit upright and loosen restrictive clothing. Use prescribed rescue bronchodilators if available.",
    "clinical_notes": "Risk of acute hypercapnic or hypoxic respiratory arrest."
  },
  {
    "rule_id": "RULE_EMERG_AIRWAY_STRIDOR",
    "version": "1.0.0",
    "description": "Inspiratory stridor or tongue/facial angioedema",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "followup_answers": {
        "QID_RESP_STRIDOR": "YES"
      }
    },
    "explanation": "Stridor indicates critical narrowing of the extrathoracic upper airway, posing an imminent danger of total airway occlusion.",
    "recommended_action": "Call emergency services immediately. If prescribed an epinephrine auto-injector, administer immediately into anterolateral thigh.",
    "clinical_notes": "Anaphylaxis or acute epiglotittic compromise."
  },
  {
    "rule_id": "RULE_EMERG_THUNDERCLAP",
    "version": "1.0.0",
    "description": "Explosive sudden-onset headache reaching maximal peak within seconds",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_SUDDEN_SEVERE_HEADACHE",
        "SYM_HEADACHE"
      ],
      "followup_answers": {
        "QID_PAIN_ONSET_SUDDEN": "YES"
      },
      "min_severity": 8
    },
    "explanation": "Thunderclap headache is the hallmark presentation of aneurysmal subarachnoid hemorrhage or cerebral venous sinus thrombosis until proven otherwise.",
    "recommended_action": "Go directly to the nearest emergency room with neuroimaging capabilities via ambulance.",
    "clinical_notes": "Non-contrast cranial CT followed by lumbar puncture if CT is negative."
  },
  {
    "rule_id": "RULE_EMERG_MENINGISMUS",
    "version": "1.0.0",
    "description": "Fever accompanied by severe neck stiffness and photophobia",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_FEVER",
        "SYM_HEADACHE"
      ],
      "followup_answers": {
        "QID_HEADACHE_STIFF_NECK": "NO"
      }
    },
    "explanation": "Nuchal rigidity in the presence of pyrexia is strongly suggestive of acute bacterial or viral central nervous system infection.",
    "recommended_action": "Immediate emergency hospitalization for diagnostic evaluation and early empiric parenteral antimicrobials.",
    "clinical_notes": "Urgent lumbar puncture and blood cultures."
  },
  {
    "rule_id": "RULE_EMERG_ACUTE_PERITONISM",
    "version": "1.0.0",
    "description": "Severe abdominal pain with board-like muscular rigidity or rebound tenderness",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_ABDOMINAL_PAIN"
      ],
      "followup_answers": {
        "QID_ABD_RIGIDITY": "YES"
      },
      "min_severity": 7
    },
    "explanation": "Generalized abdominal rigidity signals visceral perforation, peritonitis, or severe intra-abdominal catastrophe.",
    "recommended_action": "Immediate emergency surgical evaluation. Fast (do not eat or drink anything) in anticipation of urgent intervention.",
    "clinical_notes": "Immediate CT abdomen and surgical consultation."
  },
  {
    "rule_id": "RULE_EMERG_GI_HEMORRHAGE",
    "version": "1.0.0",
    "description": "Frank hematemesis, coffee-ground emesis, or profuse melena",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "followup_answers": {
        "QID_BLEEDING_SIGNS": "YES"
      }
    },
    "explanation": "Gross gastrointestinal bleeding can rapidly precipitate hypovolemic shock, particularly in patients with coagulopathies or liver disease.",
    "recommended_action": "Seek emergency medical care immediately via emergency medical services.",
    "clinical_notes": "Hemodynamic stabilization, type and cross-match, intravenous access."
  },
  {
    "rule_id": "RULE_EMERG_SYNCOPE_CARDIO",
    "version": "1.0.0",
    "description": "Sudden loss of consciousness with chest pain or palpitations",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "required_symptoms": [
        "SYM_CHEST_PAIN",
        "SYM_PALPITATIONS",
        "SYM_DIZZINESS"
      ],
      "followup_answers": {
        "QID_SYNCOPE_EPISODE": "YES"
      }
    },
    "explanation": "Syncope preceded by cardiac symptoms raises suspicion for high-grade atrioventricular block, malignant ventricular arrhythmia, or structural outflow obstruction.",
    "recommended_action": "Immediate emergency department evaluation with continuous cardiac telemetry.",
    "clinical_notes": "Continuous ECG monitoring and echocardiographic assessment."
  },
  {
    "rule_id": "RULE_EMERG_SEVERE_WORSENING_MULTIPLE",
    "version": "1.0.0",
    "description": "Multiple symptoms with high severity (>=8) and rapid worsening",
    "urgency_category": 1,
    "urgency_label": "Emergency Care",
    "conditions": {
      "min_symptoms_count": 2,
      "min_severity": 8,
      "followup_answers": {
        "QID_SYMPTOM_PROGRESSION": "WORSENING_RAPIDLY"
      }
    },
    "explanation": "Rapidly deteriorating multi-symptom illness at extreme severity indicates acute decompensation requiring emergent medical triage.",
    "recommended_action": "Contact emergency medical services or proceed immediately to the nearest Emergency Department.",
    "clinical_notes": "Rapid clinical stabilization."
  },
  {
    "rule_id": "RULE_EARLY_FEVER_IMMUNOCOMPROMISED",
    "version": "1.0.0",
    "description": "Fever in an immunocompromised host or cancer chemotherapy patient",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "required_symptoms": [
        "SYM_FEVER"
      ],
      "followup_answers": {
        "QID_IMMUNOSUPPRESSED": "YES"
      }
    },
    "explanation": "Febrile immunocompromised patients are at high risk for neutropenic bacteremia and rapid septic progression.",
    "recommended_action": "Contact your treating oncologist, hematologist, or attend urgent care/emergency within 2-4 hours for complete blood count and empiric coverage.",
    "clinical_notes": "Urgent absolute neutrophil count (ANC) determination."
  },
  {
    "rule_id": "RULE_EARLY_DVT_SUSPICION",
    "version": "1.0.0",
    "description": "Unilateral calf swelling and tenderness following surgery or prolonged immobility",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "followup_answers": {
        "QID_CALF_SWELLING": "YES"
      }
    },
    "explanation": "Asymmetric lower extremity swelling is the primary clinical finding in deep vein thrombosis, carrying risk of pulmonary embolism.",
    "recommended_action": "Seek same-day medical consultation or urgent care evaluation for bilateral compression ultrasound.",
    "clinical_notes": "Wells DVT criteria scoring and venous duplex scan."
  },
  {
    "rule_id": "RULE_EARLY_PERSISTENT_HIGH_FEVER",
    "version": "1.0.0",
    "description": "High-grade fever (>39.5\u00b0C) persisting longer than 48 hours without clear focus",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "required_symptoms": [
        "SYM_FEVER"
      ],
      "followup_answers": {
        "QID_FEVER_TEMP": "HIGH_GRADE"
      }
    },
    "explanation": "Sustained high fevers resistant to antipyretics warrant prompt laboratory investigations to identify occult bacterial foci.",
    "recommended_action": "Schedule an in-person medical evaluation within 12 to 24 hours.",
    "clinical_notes": "Urinalysis, chest radiography, and inflammatory markers."
  },
  {
    "rule_id": "RULE_EARLY_PREGNANCY_ABDOMINAL_PAIN",
    "version": "1.0.0",
    "description": "Abdominal or pelvic pain in pregnancy or early postpartum period",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "required_symptoms": [
        "SYM_ABDOMINAL_PAIN"
      ],
      "followup_answers": {
        "QID_PREGNANCY_STATUS": "PREGNANT"
      }
    },
    "explanation": "Pelvic pain in pregnant individuals requires exclusion of ectopic gestation, placental abruption, or pre-eclampsia with hepatic capsule distension.",
    "recommended_action": "Contact your obstetrician/gynecologist or go to an obstetric triage unit today.",
    "clinical_notes": "Transvaginal ultrasound and beta-hCG correlation."
  },
  {
    "rule_id": "RULE_EARLY_HEAD_TRAUMA_CONCUSSION",
    "version": "1.0.0",
    "description": "Headache, nausea, or dizziness following direct head impact within 48 hours",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "required_symptoms": [
        "SYM_HEADACHE",
        "SYM_DIZZINESS"
      ],
      "followup_answers": {
        "QID_TRAUMA_HEAD": "YES"
      }
    },
    "explanation": "Post-traumatic symptoms require assessment using clinical decision rules (such as Canadian CT Head Rule) to exclude delayed intracranial bleeding.",
    "recommended_action": "Undergo professional medical assessment today. Avoid physical exertion and screens. Have a companion monitor for decreasing alertness.",
    "clinical_notes": "Canadian CT Head Rule application."
  },
  {
    "rule_id": "RULE_EARLY_MODERATE_PROGRESSING",
    "version": "1.0.0",
    "description": "Moderate severity symptoms (5-7) worsening despite conservative management",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "min_severity": 5,
      "max_severity": 7,
      "followup_answers": {
        "QID_SYMPTOM_PROGRESSION": "WORSENING_SLOWLY"
      }
    },
    "explanation": "A steadily worsening symptom trajectory suggests an evolving pathology that has not resolved spontaneously.",
    "recommended_action": "Arrange an appointment with your primary care provider or visit a walk-in urgent care center within 24 to 48 hours.",
    "clinical_notes": "Comprehensive clinical review and targeted diagnostic workup."
  },
  {
    "rule_id": "RULE_EARLY_VISUAL_DISTURBANCE",
    "version": "1.0.0",
    "description": "New headache with blurred or double vision",
    "urgency_category": 2,
    "urgency_label": "Early Medical Consultation",
    "conditions": {
      "required_symptoms": [
        "SYM_HEADACHE"
      ],
      "followup_answers": {
        "QID_HEADACHE_VISION": "YES"
      }
    },
    "explanation": "Headaches coupled with diplopia or scotoma necessitate fundoscopic examination to rule out papilledema or temporal arteritis in older patients.",
    "recommended_action": "Seek prompt medical evaluation by an eye care specialist or physician within 24 hours.",
    "clinical_notes": "Fundoscopy and visual field testing."
  },
  {
    "rule_id": "RULE_ROUTINE_MILD_ISOLATED",
    "version": "1.0.0",
    "description": "Mild isolated symptom (severity <= 3) of short or moderate duration",
    "urgency_category": 3,
    "urgency_label": "Routine Healthcare",
    "conditions": {
      "max_severity": 3,
      "followup_answers": {
        "QID_SYMPTOM_PROGRESSION": "UNCHANGED"
      }
    },
    "explanation": "Symptoms at this severity level without warning signs or progressive deterioration are generally suitable for standard outpatient evaluation or guided self-care.",
    "recommended_action": "Monitor symptoms, rest, maintain adequate hydration. Schedule a routine primary care visit if symptoms persist or do not improve after 5-7 days.",
    "clinical_notes": "Conservative supportive measures; follow-up if signs change."
  },
  {
    "rule_id": "RULE_ROUTINE_IMPROVING",
    "version": "1.0.0",
    "description": "Symptoms actively improving with resolving severity",
    "urgency_category": 3,
    "urgency_label": "Routine Healthcare",
    "conditions": {
      "followup_answers": {
        "QID_SYMPTOM_PROGRESSION": "IMPROVING"
      }
    },
    "explanation": "An improving trajectory indicates that the physiological response or home measures are effectively managing the condition.",
    "recommended_action": "Continue current supportive measures and rest. Contact a healthcare provider on a non-urgent basis if recovery stalls or symptoms relapse.",
    "clinical_notes": "Reassure patient with clear red-flag return instructions."
  },
  {
    "rule_id": "RULE_ROUTINE_CHRONIC_STABLE",
    "version": "1.0.0",
    "description": "Stable chronic symptom of over 1 week duration with mild to moderate severity",
    "urgency_category": 3,
    "urgency_label": "Routine Healthcare",
    "conditions": {
      "max_severity": 5,
      "followup_answers": {
        "QID_SYMPTOM_DURATION": "WEEKS",
        "QID_SYMPTOM_PROGRESSION": "UNCHANGED"
      }
    },
    "explanation": "Long-standing stable symptoms without acute acceleration or systemic features are best addressed through a planned comprehensive primary care consultation.",
    "recommended_action": "Book a routine appointment with your regular doctor or specialist for maintenance review and treatment optimization.",
    "clinical_notes": "Review chronic disease management plan."
  },
  {
    "rule_id": "RULE_INSUFFICIENT_CONTRADICTORY",
    "version": "1.0.0",
    "description": "Contradictory information (e.g. reported extreme severity but also marked as completely resolving)",
    "urgency_category": 4,
    "urgency_label": "Insufficient Information",
    "conditions": {
      "contradiction_detected": true
    },
    "explanation": "The information provided contains conflicting or mutually exclusive responses that prevent a coherent, safe triage determination.",
    "recommended_action": "Please re-read and answer the assessment questions carefully, or contact a healthcare helpline (e.g., NHS 111 / telehealth) for interactive triage with a registered clinician.",
    "clinical_notes": "Clinical reassessment required due to discordant user responses."
  },
  {
    "rule_id": "RULE_INSUFFICIENT_DATA_INCOMPLETE",
    "version": "1.0.0",
    "description": "Incomplete assessment with missing critical red-flag responses",
    "urgency_category": 4,
    "urgency_label": "Insufficient Information",
    "conditions": {
      "missing_critical_answers": true
    },
    "explanation": "Essential safety questions were bypassed or omitted. A valid urgency assessment cannot safely be rendered without this data.",
    "recommended_action": "Complete the required follow-up questions to receive a valid classification. If in doubt about severe symptoms, always err on the side of seeking medical care.",
    "clinical_notes": "Incomplete dataset prevents automated risk stratification."
  }
];

export const BUNDLED_WARNING_SIGNS = [
  {
    "code": "WARN_CHEST_RADIATION",
    "name": "Chest Pain Radiating to Left Arm, Jaw, or Back",
    "category": "cardiovascular",
    "urgency_override": 1,
    "description": "Pressure, squeezing, fullness or pain in the center of the chest that radiates to shoulders, neck, jaw, or arms.",
    "associated_conditions": [
      "Acute Coronary Syndrome",
      "Myocardial Infarction"
    ],
    "action_required": "Call emergency medical services immediately (e.g. 911 / 112 / 999). Rest quietly while awaiting help.",
    "red_flag": true
  },
  {
    "code": "WARN_STROKE_FAST",
    "name": "Facial Droop, Arm Weakness, or Slurred Speech (FAST)",
    "category": "neurological",
    "urgency_override": 1,
    "description": "Sudden unilateral facial droop, inability to raise both arms equally, or slurred/incomprehensible speech.",
    "associated_conditions": [
      "Acute Ischemic Stroke",
      "Intracranial Hemorrhage"
    ],
    "action_required": "Call emergency services immediately. Note exact time symptoms began (crucial for thrombolytic window).",
    "red_flag": true
  },
  {
    "code": "WARN_RESP_DISTRESS_SEVERE",
    "name": "Severe Respiratory Distress / Inability to Speak Full Sentences",
    "category": "respiratory",
    "urgency_override": 1,
    "description": "Extreme shortness of breath with cyanosis (blue lips/fingers), intercostal retractions, or gasping.",
    "associated_conditions": [
      "Severe Asthma Exacerbation",
      "Pulmonary Embolism",
      "Pneumothorax"
    ],
    "action_required": "Activate emergency response immediately. Maintain sitting upright position.",
    "red_flag": true
  },
  {
    "code": "WARN_ANAPHYLAXIS",
    "name": "Anaphylaxis / Airway Compromise with Stridor or Tongue Swelling",
    "category": "immunological",
    "urgency_override": 1,
    "description": "Rapidly developing allergic reaction with tongue/throat swelling, hoarseness, stridor, or hypotension.",
    "associated_conditions": [
      "Severe Anaphylaxis"
    ],
    "action_required": "Administer intramuscular epinephrine auto-injector if prescribed and available. Call emergency services immediately.",
    "red_flag": true
  },
  {
    "code": "WARN_THUNDERCLAP_HEADACHE",
    "name": "Thunderclap Headache (Worst Headache of Life)",
    "category": "neurological",
    "urgency_override": 1,
    "description": "Headache reaching peak intensity in under one minute, often described as a catastrophic blow to the head.",
    "associated_conditions": [
      "Subarachnoid Hemorrhage"
    ],
    "action_required": "Emergency Department evaluation immediately via emergency medical transport.",
    "red_flag": true
  },
  {
    "code": "WARN_UNCONTROLLED_HEMORRHAGE",
    "name": "Uncontrolled Pulsatile or Severe External Hemorrhage",
    "category": "trauma",
    "urgency_override": 1,
    "description": "Active bleeding from a major blood vessel that does not stop with direct sustained pressure.",
    "associated_conditions": [
      "Arterial Laceration",
      "Vascular Trauma"
    ],
    "action_required": "Apply firm direct continuous pressure; use commercial tourniquet if extremity and trained. Call emergency services.",
    "red_flag": true
  },
  {
    "code": "WARN_SEIZURE_PROLONGED",
    "name": "Prolonged Seizure (>5 minutes) or Status Epilepticus",
    "category": "neurological",
    "urgency_override": 1,
    "description": "Continuous generalized seizure activity lasting more than 5 minutes or repeated seizures without regaining consciousness.",
    "associated_conditions": [
      "Status Epilepticus"
    ],
    "action_required": "Protect patient from physical injury; do not put anything in mouth; position on side; call emergency services immediately.",
    "red_flag": true
  },
  {
    "code": "WARN_SYNCOPE_EXERTIONAL",
    "name": "Sudden Collapse or Loss of Consciousness During Exertion",
    "category": "cardiovascular",
    "urgency_override": 1,
    "description": "Fainting or sudden cardiac arrest occurring during physical exertion or exercise.",
    "associated_conditions": [
      "Cardiac Arrhythmia",
      "Hypertrophic Cardiomyopathy",
      "Aortic Stenosis"
    ],
    "action_required": "Check responsiveness and breathing; begin CPR and use AED if pulseless; call emergency services immediately.",
    "red_flag": true
  },
  {
    "code": "WARN_SHOCK_SIGNS",
    "name": "Signs of Systemic Shock (Cold Clammy Skin, Marked Confusion, Tachycardia)",
    "category": "systemic",
    "urgency_override": 1,
    "description": "Profound circulatory collapse: systolic blood pressure very low, extreme pallor, rapid thready pulse, oliguria.",
    "associated_conditions": [
      "Septic Shock",
      "Hypovolemic Shock",
      "Cardiogenic Shock"
    ],
    "action_required": "Call emergency services immediately. Keep patient warm and supine with legs slightly elevated if tolerated.",
    "red_flag": true
  },
  {
    "code": "WARN_ACUTE_ABDOMEN_RIGID",
    "name": "Board-like Rigid Abdomen with Involuntary Guarding",
    "category": "gastrointestinal",
    "urgency_override": 1,
    "description": "Severe abdominal pain accompanied by generalized rigidity of abdominal muscles that cannot be voluntarily relaxed.",
    "associated_conditions": [
      "Visceral Perforation",
      "Peritonitis"
    ],
    "action_required": "Emergency surgical evaluation required. Patient should not consume food or water.",
    "red_flag": true
  },
  {
    "code": "WARN_SUDDEN_VISION_LOSS",
    "name": "Sudden Painless or Painful Loss of Vision in One or Both Eyes",
    "category": "ophthalmic",
    "urgency_override": 1,
    "description": "Sudden complete darkness, curtain falling across vision field, or loss of central vision.",
    "associated_conditions": [
      "Central Retinal Artery Occlusion",
      "Retinal Detachment",
      "Temporal Arteritis"
    ],
    "action_required": "Immediate emergency ophthalmology evaluation within hours to prevent irreversible vision loss.",
    "red_flag": true
  },
  {
    "code": "WARN_HEMATEMESIS",
    "name": "Vomiting Bright Red Blood or Dark 'Coffee-Ground' Material",
    "category": "gastrointestinal",
    "urgency_override": 1,
    "description": "Vomiting frank red blood or partially digested blood resembling dark coffee grounds in volume.",
    "associated_conditions": [
      "Upper Gastrointestinal Bleed",
      "Esophageal Variceal Hemorrhage"
    ],
    "action_required": "Emergency Department evaluation immediately via emergency medical transport.",
    "red_flag": true
  },
  {
    "code": "WARN_HEMOPTYSIS_MASSIVE",
    "name": "Coughing Up Moderate to Large Volumes of Blood (>100 mL)",
    "category": "respiratory",
    "urgency_override": 1,
    "description": "Coughing up fresh blood from the respiratory tract indicating pulmonary vascular breach.",
    "associated_conditions": [
      "Massive Hemoptysis",
      "Pulmonary Infarction",
      "Bronchiectasis"
    ],
    "action_required": "Immediate emergency evaluation; position on affected side if known to prevent aspiration.",
    "red_flag": true
  },
  {
    "code": "WARN_SUICIDALITY_ACUTE",
    "name": "Acute Suicidal Ideation with Intent or Immediate Plan",
    "category": "psychiatric",
    "urgency_override": 1,
    "description": "Expressed thoughts of immediate self-harm with identified means or active suicidal gesture.",
    "associated_conditions": [
      "Acute Psychiatric Crisis"
    ],
    "action_required": "Do not leave patient alone. Call emergency services or national suicide prevention lifeline (988 in US / local crisis line).",
    "red_flag": true
  },
  {
    "code": "WARN_MENINGEAL_SIGNS",
    "name": "High Fever with Inability to Touch Chin to Chest (Nuchal Rigidity)",
    "category": "neurological",
    "urgency_override": 1,
    "description": "Severe neck stiffness preventing neck flexion, accompanied by high fever and altered mental state.",
    "associated_conditions": [
      "Bacterial Meningitis"
    ],
    "action_required": "Emergency room assessment immediately for urgent diagnostic lumbar puncture and antibiotics.",
    "red_flag": true
  },
  {
    "code": "WARN_PURPURA_NONBLANCHING",
    "name": "Rapidly Spreading Non-Blanching Purple Rash (Petechiae / Purpura)",
    "category": "dermatological",
    "urgency_override": 1,
    "description": "Purple or red spots that do not fade or turn white when pressed firmly with a clear glass tumbler.",
    "associated_conditions": [
      "Meningococcal Septicemia",
      "Thrombotic Microangiopathy"
    ],
    "action_required": "Immediate emergency hospitalization.",
    "red_flag": true
  },
  {
    "code": "WARN_ACUTE_URINARY_RETENTION",
    "name": "Complete Inability to Pass Urine with Painful Palpable Bladder",
    "category": "urological",
    "urgency_override": 2,
    "description": "Distressing lower abdominal pain with complete cessation of urination over 8-12 hours.",
    "associated_conditions": [
      "Acute Urinary Retention"
    ],
    "action_required": "Prompt emergency or urgent care decompression with Foley catheterization.",
    "red_flag": false
  },
  {
    "code": "WARN_TESTICULAR_TORSION",
    "name": "Sudden Severe Unilateral Testicular Pain with Swelling",
    "category": "urological",
    "urgency_override": 1,
    "description": "Acute onset of high-intensity scrotal pain, swelling, and elevation of testis.",
    "associated_conditions": [
      "Testicular Torsion"
    ],
    "action_required": "Immediate surgical evaluation within 6 hours to preserve testicular viability.",
    "red_flag": true
  },
  {
    "code": "WARN_ECTOPIC_PREGNANCY",
    "name": "Severe Lower Pelvic Pain with Vaginal Bleeding and Positive Pregnancy",
    "category": "obstetric",
    "urgency_override": 1,
    "description": "Unilateral pelvic pain, dizziness, or shoulder-tip pain in a female of reproductive age.",
    "associated_conditions": [
      "Ruptured Ectopic Pregnancy"
    ],
    "action_required": "Immediate emergency evaluation for life-threatening hemoperitoneum.",
    "red_flag": true
  },
  {
    "code": "WARN_HYPOGLYCEMIA_SEVERE",
    "name": "Severe Hypoglycemia with Inability to Cooperate or Seizure",
    "category": "endocrine",
    "urgency_override": 1,
    "description": "Severe low blood glucose in diabetic patient unresponsive to oral carbohydrates or unable to swallow.",
    "associated_conditions": [
      "Severe Hypoglycemia"
    ],
    "action_required": "Administer intramuscular glucagon if trained; call emergency services.",
    "red_flag": true
  },
  {
    "code": "WARN_DVT_PE",
    "name": "Unilateral Swollen Painful Calf Following Prolonged Inactivity or Surgery",
    "category": "cardiovascular",
    "urgency_override": 2,
    "description": "Marked swelling, erythema, and warmth in one leg, especially with recent immobilization.",
    "associated_conditions": [
      "Deep Vein Thrombosis",
      "Risk of Pulmonary Embolism"
    ],
    "action_required": "Same-day urgent medical evaluation with venous duplex ultrasonography.",
    "red_flag": false
  },
  {
    "code": "WARN_HIGH_FEVER_INFANT",
    "name": "Fever >= 38.0\u00b0C (100.4\u00b0F) in Infant Under 3 Months of Age",
    "category": "pediatric",
    "urgency_override": 1,
    "description": "Any documented fever in a neonate or young infant, who have immature immune responses.",
    "associated_conditions": [
      "Neonatal Sepsis",
      "Occult Bacteremia"
    ],
    "action_required": "Immediate pediatric emergency evaluation; do not wait.",
    "red_flag": true
  },
  {
    "code": "WARN_CARBON_MONOXIDE",
    "name": "Simultaneous Headache, Nausea, and Confusion in Multiple Household Members",
    "category": "toxicology",
    "urgency_override": 1,
    "description": "Shared symptoms occurring in an enclosed space with fuel-burning heaters or generators.",
    "associated_conditions": [
      "Carbon Monoxide Poisoning"
    ],
    "action_required": "Evacuate the structure immediately into fresh air and contact emergency services.",
    "red_flag": true
  },
  {
    "code": "WARN_HEATSTROKE",
    "name": "Body Temperature > 40\u00b0C (104\u00b0F) with Hot Dry Skin and Delirium",
    "category": "environmental",
    "urgency_override": 1,
    "description": "Thermoregulatory failure following heat exposure; altered sensorium, lack of sweating.",
    "associated_conditions": [
      "Exertional / Classic Heatstroke"
    ],
    "action_required": "Call emergency services; initiate rapid aggressive active cooling with cold water / ice immersion.",
    "red_flag": true
  },
  {
    "code": "WARN_HYPOTHERMIA_SEVERE",
    "name": "Severe Shivering Followed by Apathy, Slurred Speech, and Paradoxical Undressing",
    "category": "environmental",
    "urgency_override": 1,
    "description": "Core body temperature dropping critically low with cessation of shivering and confusion.",
    "associated_conditions": [
      "Severe Accidental Hypothermia"
    ],
    "action_required": "Gentle handling, passive and active rewarming, emergency transport.",
    "red_flag": true
  },
  {
    "code": "WARN_OCULAR_CHEMICAL_BURN",
    "name": "Acid or Alkali Chemical Splash Directly into Eye",
    "category": "ophthalmic",
    "urgency_override": 1,
    "description": "Contact with caustic cleaning products, battery fluid, or cement.",
    "associated_conditions": [
      "Corneal Caustic Injury"
    ],
    "action_required": "Immediately irrigate eye continuously with clean tap water or saline for at least 15-30 minutes; call emergency services.",
    "red_flag": true
  },
  {
    "code": "WARN_MAJOR_BURN",
    "name": "Second or Third Degree Burns Covering >10% Body Area or Involving Face/Hands",
    "category": "trauma",
    "urgency_override": 1,
    "description": "Extensive blistering, charred, or leathery white tissue damage.",
    "associated_conditions": [
      "Major Thermal Burn Injury"
    ],
    "action_required": "Cover with clean dry non-adherent dressing; keep warm; transport to burn center via EMS.",
    "red_flag": true
  },
  {
    "code": "WARN_FRACTURE_OPEN",
    "name": "Deformed Limb with Bone Fragment Piercing Through Skin",
    "category": "musculoskeletal",
    "urgency_override": 1,
    "description": "High-energy extremity injury with open dermal wound communicating with fracture.",
    "associated_conditions": [
      "Open / Compound Fracture"
    ],
    "action_required": "Cover with sterile dressing, immobilize without manipulation, emergency department transfer.",
    "red_flag": true
  },
  {
    "code": "WARN_HEAD_TRAUMA_LUCID",
    "name": "Head Injury with Loss of Consciousness, Brief Awakening, then Rapid Deterioration",
    "category": "neurological",
    "urgency_override": 1,
    "description": "The classic 'lucid interval' indicative of rapid intracranial arterial accumulation.",
    "associated_conditions": [
      "Epidural Hematoma"
    ],
    "action_required": "Immediate neurosurgical emergency evaluation.",
    "red_flag": true
  },
  {
    "code": "WARN_COMPARTMENT_SYNDROME",
    "name": "Pain Out of Proportion to Injury with Tense Swelling and Paresthesia",
    "category": "musculoskeletal",
    "urgency_override": 1,
    "description": "Intense pain on passive muscle stretching, firm fascial compartment.",
    "associated_conditions": [
      "Acute Compartment Syndrome"
    ],
    "action_required": "Emergency fasciotomy consultation required within hours.",
    "red_flag": true
  },
  {
    "code": "WARN_CAUDA_EQUINA",
    "name": "Back Pain with Saddle Anesthesia (Numb Groin) and Fecal/Urinary Incontinence",
    "category": "neurological",
    "urgency_override": 1,
    "description": "Compression of cauda equina nerve roots causing perineal sensory loss and sphincter dysfunction.",
    "associated_conditions": [
      "Cauda Equina Syndrome"
    ],
    "action_required": "Emergency MRI and decompression within 24-48 hours to prevent permanent deficit.",
    "red_flag": true
  },
  {
    "code": "WARN_JAUNDICE_FEVER",
    "name": "Yellow Skin/Eyes (Jaundice) with Spiking High Fever and Right Upper Quadrant Pain",
    "category": "gastrointestinal",
    "urgency_override": 1,
    "description": "Charcot's triad indicating acute purulent infection of the biliary tree.",
    "associated_conditions": [
      "Acute Ascending Cholangitis"
    ],
    "action_required": "Immediate hospitalization for resuscitation and urgent biliary decompression.",
    "red_flag": true
  },
  {
    "code": "WARN_HYPERTENSIVE_CRISIS",
    "name": "Blood Pressure > 180/120 mmHg Accompanied by Headache, Chest Pain, or Dyspnea",
    "category": "cardiovascular",
    "urgency_override": 1,
    "description": "Extremely elevated blood pressure with evidence of acute end-organ damage.",
    "associated_conditions": [
      "Hypertensive Emergency"
    ],
    "action_required": "Emergency room treatment with intravenous antihypertensive medications.",
    "red_flag": true
  },
  {
    "code": "WARN_ACUTE_GLAUCOMA",
    "name": "Severe Eye Pain, Colored Halos Around Lights, and Hazy Cornea",
    "category": "ophthalmic",
    "urgency_override": 1,
    "description": "Rapid spike in intraocular pressure causing globe tenderness, nausea, and visual distortion.",
    "associated_conditions": [
      "Acute Angle-Closure Glaucoma"
    ],
    "action_required": "Emergency ophthalmic pressure-reducing drops and systemic medications.",
    "red_flag": true
  },
  {
    "code": "WARN_DIABETIC_KETOACIDOSIS",
    "name": "Deep Rapid Breathing (Kussmaul), Fruity Acetone Breath, and Vomiting in Diabetic",
    "category": "endocrine",
    "urgency_override": 1,
    "description": "Metabolic acidosis resulting from severe insulin deficiency.",
    "associated_conditions": [
      "Diabetic Ketoacidosis (DKA)"
    ],
    "action_required": "Emergency hospital admission for intravenous insulin and electrolyte replacement.",
    "red_flag": true
  },
  {
    "code": "WARN_PNEUMOTHORAX_TENSION",
    "name": "Sudden Sharp Pleuritic Chest Pain with Tracheal Deviation and Cyanosis",
    "category": "respiratory",
    "urgency_override": 1,
    "description": "Air trapped under pressure in pleural cavity causing mediastinal shift and vascular collapse.",
    "associated_conditions": [
      "Tension Pneumothorax"
    ],
    "action_required": "Immediate emergency needle decompression followed by tube thoracostomy.",
    "red_flag": true
  },
  {
    "code": "WARN_SEPSIS_SCREEN_POSITIVE",
    "name": "Infection Signs with Tachypnea, Altered Consciousness, and Low Blood Pressure",
    "category": "systemic",
    "urgency_override": 1,
    "description": "Dysregulated host response to infection causing life-threatening organ dysfunction (qSOFA >= 2).",
    "associated_conditions": [
      "Severe Sepsis"
    ],
    "action_required": "Immediate medical emergency: blood cultures, broad-spectrum antibiotics, and IV crystalloids.",
    "red_flag": true
  },
  {
    "code": "WARN_MELENA",
    "name": "Jet-Black, Tarry, Foul-Smelling Stools",
    "category": "gastrointestinal",
    "urgency_override": 2,
    "description": "Oxidized hemoglobin from significant upper gastrointestinal tract bleeding.",
    "associated_conditions": [
      "Upper GI Bleeding",
      "Peptic Ulcer Bleed"
    ],
    "action_required": "Urgent same-day medical assessment or emergency visit if accompanied by dizziness.",
    "red_flag": false
  },
  {
    "code": "WARN_FOREIGN_BODY_AIRWAY",
    "name": "Sudden Choking with Inability to Speak, Cough, or Breathe",
    "category": "respiratory",
    "urgency_override": 1,
    "description": "Complete mechanical obstruction of upper airway by food or foreign object.",
    "associated_conditions": [
      "Foreign Body Airway Obstruction"
    ],
    "action_required": "Immediate Heimlich maneuver (abdominal thrusts) or back blows / chest thrusts; call emergency services.",
    "red_flag": true
  },
  {
    "code": "WARN_RAPID_CELLULITIS",
    "name": "Red, Swollen Skin Lesion Expanding Visibly Within Hours with Crepitus",
    "category": "dermatological",
    "urgency_override": 1,
    "description": "Disproportionate soft tissue pain, bullae, skin anesthesia, or crackling gas sensation.",
    "associated_conditions": [
      "Necrotizing Fasciitis"
    ],
    "action_required": "Surgical emergency consultation for immediate debridement and parenteral antibiotics.",
    "red_flag": true
  }
];

export const BUNDLED_FACILITIES = [
  {
    "id": "IN_MUM_001",
    "name": "King Edward Memorial (KEM) Hospital",
    "facility_type": "Government Medical College Hospital",
    "locality": "Parel",
    "city": "Mumbai",
    "district": "Mumbai City",
    "state": "Maharashtra",
    "pincode": "400012",
    "latitude": 19.0033,
    "longitude": 72.8427,
    "phone": "+91-22-2410-7000",
    "emergency_helpline": "112 / 102 / 108",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 1800,
    "ownership": "Municipal"
  },
  {
    "id": "IN_MUM_002",
    "name": "Sir J.J. Group of Hospitals",
    "facility_type": "State Government Tertiary Hospital",
    "locality": "Byculla",
    "city": "Mumbai",
    "district": "Mumbai City",
    "state": "Maharashtra",
    "pincode": "400008",
    "latitude": 18.9634,
    "longitude": 72.8341,
    "phone": "+91-22-2373-5555",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 2844,
    "ownership": "Government"
  },
  {
    "id": "IN_MUM_003",
    "name": "Lilavati Hospital and Research Centre",
    "facility_type": "Multi-Speciality Tertiary Care Hospital",
    "locality": "Bandra West",
    "city": "Mumbai",
    "district": "Mumbai Suburban",
    "state": "Maharashtra",
    "pincode": "400050",
    "latitude": 19.0514,
    "longitude": 72.8294,
    "phone": "+91-22-2675-1000",
    "emergency_helpline": "+91-22-2656-8000 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 323,
    "ownership": "Trust"
  },
  {
    "id": "IN_MUM_004",
    "name": "Kokilaben Dhirubhai Ambani Hospital",
    "facility_type": "Quaternary Care & Level 1 Trauma Center",
    "locality": "Andheri West",
    "city": "Mumbai",
    "district": "Mumbai Suburban",
    "state": "Maharashtra",
    "pincode": "400053",
    "latitude": 19.1311,
    "longitude": 72.8251,
    "phone": "+91-22-4269-6969",
    "emergency_helpline": "+91-22-4269-9999 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 750,
    "ownership": "Private"
  },
  {
    "id": "IN_MUM_005",
    "name": "Dr. R. N. Cooper Municipal General Hospital",
    "facility_type": "Municipal Medical College Hospital",
    "locality": "Vile Parle West",
    "city": "Mumbai",
    "district": "Mumbai Suburban",
    "state": "Maharashtra",
    "pincode": "400056",
    "latitude": 19.1082,
    "longitude": 72.8365,
    "phone": "+91-22-2620-7254",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 636,
    "ownership": "Municipal"
  },
  {
    "id": "IN_MUM_006",
    "name": "Hinduja National Hospital",
    "facility_type": "Multi-Speciality Tertiary Hospital",
    "locality": "Mahim",
    "city": "Mumbai",
    "district": "Mumbai City",
    "state": "Maharashtra",
    "pincode": "400016",
    "latitude": 19.0335,
    "longitude": 72.8384,
    "phone": "+91-22-2445-1515",
    "emergency_helpline": "+91-22-2445-2222 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 400,
    "ownership": "Trust"
  },
  {
    "id": "IN_PUN_001",
    "name": "Sassoon General Hospital & B.J. Medical College",
    "facility_type": "State Government Tertiary Hospital",
    "locality": "Sassoon Road",
    "city": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "pincode": "411001",
    "latitude": 18.5262,
    "longitude": 73.8732,
    "phone": "+91-20-2612-8000",
    "emergency_helpline": "112 / 102 / 108",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 1296,
    "ownership": "Government"
  },
  {
    "id": "IN_PUN_002",
    "name": "Ruby Hall Clinic",
    "facility_type": "Multi-Speciality Tertiary Care Hospital",
    "locality": "Sassoon Road",
    "city": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "pincode": "411001",
    "latitude": 18.5323,
    "longitude": 73.8785,
    "phone": "+91-20-6645-5100",
    "emergency_helpline": "+91-20-2616-3391 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 600,
    "ownership": "Trust"
  },
  {
    "id": "IN_PUN_003",
    "name": "Deenanath Mangeshkar Hospital",
    "facility_type": "Multi-Speciality Hospital and Research Center",
    "locality": "Erandwane",
    "city": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "pincode": "411004",
    "latitude": 18.5028,
    "longitude": 73.8322,
    "phone": "+91-20-4015-1000",
    "emergency_helpline": "+91-20-4015-1600 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 900,
    "ownership": "Trust"
  },
  {
    "id": "IN_THA_001",
    "name": "Chhatrapati Shivaji Maharaj Hospital",
    "facility_type": "Municipal Medical College Hospital",
    "locality": "Kalwa",
    "city": "Thane",
    "district": "Thane",
    "state": "Maharashtra",
    "pincode": "400605",
    "latitude": 19.1982,
    "longitude": 72.9984,
    "phone": "+91-22-2537-2580",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 500,
    "ownership": "Municipal"
  },
  {
    "id": "IN_NAV_001",
    "name": "Apollo Hospitals Navi Mumbai",
    "facility_type": "Quaternary Care Hospital",
    "locality": "CBD Belapur",
    "city": "Navi Mumbai",
    "district": "Thane",
    "state": "Maharashtra",
    "pincode": "400614",
    "latitude": 19.0182,
    "longitude": 73.0416,
    "phone": "+91-22-3350-3350",
    "emergency_helpline": "1066 / 112",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 500,
    "ownership": "Private"
  },
  {
    "id": "IN_NAS_001",
    "name": "Nashik Civil Hospital",
    "facility_type": "District Civil Hospital",
    "locality": "Trimbak Road",
    "city": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "pincode": "422002",
    "latitude": 19.9975,
    "longitude": 73.7898,
    "phone": "+91-253-257-2038",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 550,
    "ownership": "Government"
  },
  {
    "id": "IN_NAG_001",
    "name": "Government Medical College and Hospital (GMCH)",
    "facility_type": "State Government Tertiary Hospital",
    "locality": "Medical Square, Hanuman Nagar",
    "city": "Nagpur",
    "district": "Nagpur",
    "state": "Maharashtra",
    "pincode": "440003",
    "latitude": 21.1352,
    "longitude": 79.0967,
    "phone": "+91-712-274-3588",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 1400,
    "ownership": "Government"
  },
  {
    "id": "IN_MUM_007",
    "name": "Nanavati Max Super Speciality Hospital",
    "facility_type": "Quaternary Care Hospital",
    "locality": "Vile Parle West",
    "city": "Mumbai",
    "district": "Mumbai Suburban",
    "state": "Maharashtra",
    "pincode": "400056",
    "latitude": 19.0991,
    "longitude": 72.8407,
    "phone": "+91-22-2626-7500",
    "emergency_helpline": "112 / 102",
    "has_emergency": true,
    "has_icu": true,
    "has_trauma_care": true,
    "beds_count": 350,
    "ownership": "Private"
  }
];
