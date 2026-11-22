import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { ProgressBar } from "../components/assessment/ProgressBar";
import { QuestionCard } from "../components/assessment/QuestionCard";
import { PainSlider } from "../components/assessment/PainSlider";
import { apiClient } from "../api/client";
import { AsyncStorageWrapper } from "../storage/asyncStorage";
import {
  SymptomOption,
  FollowUpQuestion,
  TriageAssessmentInput,
  AssessmentResult
} from "../../shared/types";

interface SymptomAssessmentScreenProps {
  navigation: any;
}

const COMMON_SYMPTOMS = [
  { id: "chest_pain", name: "Chest Pain", category: "Cardiovascular" },
  { id: "shortness_of_breath", name: "Shortness of Breath", category: "Respiratory" },
  { id: "fever", name: "High Fever", category: "General" },
  { id: "severe_headache", name: "Severe Headache", category: "Neurological" },
  { id: "abdominal_pain", name: "Abdominal Pain", category: "Gastrointestinal" },
  { id: "cough", name: "Persistent Cough", category: "Respiratory" },
  { id: "dizziness", name: "Dizziness or Vertigo", category: "Neurological" },
  { id: "nausea_vomiting", name: "Nausea & Vomiting", category: "Gastrointestinal" },
  { id: "palpitations", name: "Rapid Heartbeat / Palpitations", category: "Cardiovascular" },
  { id: "joint_pain", name: "Severe Joint Pain", category: "Musculoskeletal" }
];

const DURATION_OPTIONS = [
  { label: "< 1 hour", value: 1 },
  { label: "1 - 6 hours", value: 4 },
  { label: "6 - 24 hours", value: 12 },
  { label: "1 - 3 days", value: 48 },
  { label: "> 3 days", value: 96 }
];

const PROGRESSION_OPTIONS = [
  { label: "Worsening rapidly", value: "worsening" },
  { label: "Unchanged / Constant", value: "unchanged" },
  { label: "Improving", value: "improving" }
];

export const SymptomAssessmentScreen: React.FC<SymptomAssessmentScreenProps> = ({ navigation }) => {
  // Step tracker: 1 = Chief Symptom, 2 = Severity, 3 = Duration & Progression, 4 = Adaptive Questions, 5 = Warning Signs
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);

  // All available symptoms
  const [allSymptoms, setAllSymptoms] = useState<SymptomOption[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  // Assessment inputs
  const [selectedSymptom, setSelectedSymptom] = useState<string>("");
  const [painLevel, setPainLevel] = useState<number>(5);
  const [durationHours, setDurationHours] = useState<number>(4);
  const [progression, setProgression] = useState<string>("unchanged");

  // Adaptive questions state
  const [activeQuestion, setActiveQuestion] = useState<FollowUpQuestion | null>(null);
  const [answeredQuestions, setAnsweredQuestions] = useState<{ [qId: string]: any }>({});
  const [questionHistory, setQuestionHistory] = useState<FollowUpQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [currentSelectedAnswer, setCurrentSelectedAnswer] = useState<any>(null);

  // Warning signs state
  const [availableWarningSigns, setAvailableWarningSigns] = useState<string[]>([]);
  const [selectedWarningSigns, setSelectedWarningSigns] = useState<string[]>([]);

  useEffect(() => {
    loadSymptoms();
  }, []);

  const loadSymptoms = async () => {
    try {
      const symptoms = await apiClient.getSymptoms();
      setAllSymptoms(symptoms);
    } catch (err) {
      console.warn("Failed to load symptoms", err);
    }
  };

  // Step 1: Select Chief Symptom
  const handleSelectSymptom = (symptomId: string) => {
    setSelectedSymptom(symptomId);
    setStep(2); // Move to pain level
  };

  // Step 2 -> Step 3: Pain Severity to Duration
  const handleConfirmPain = () => {
    setStep(3);
  };

  // Step 3 -> Step 4: Duration to Adaptive Questions
  const handleStartAdaptiveQuestions = async () => {
    setLoading(true);
    try {
      const firstQ = await apiClient.getNextQuestion(selectedSymptom, {});
      if (firstQ) {
        setActiveQuestion(firstQ);
        setQuestionHistory([firstQ]);
        setCurrentQuestionIndex(0);
        setCurrentSelectedAnswer(null);
        setStep(4);
      } else {
        // No adaptive questions needed for this symptom, go straight to warning signs
        moveToWarningSigns();
      }
    } catch (err) {
      console.warn("Error starting questions", err);
      moveToWarningSigns();
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Answer Question and get Next Question
  const handleAnswerQuestion = async () => {
    if (currentSelectedAnswer === null || currentSelectedAnswer === undefined) {
      Alert.alert("Select an option", "Please select an answer to continue.");
      return;
    }

    if (!activeQuestion) return;

    const updatedAnswers = {
      ...answeredQuestions,
      [activeQuestion.id]: currentSelectedAnswer
    };
    setAnsweredQuestions(updatedAnswers);

    setLoading(true);
    try {
      const nextQ = await apiClient.getNextQuestion(selectedSymptom, updatedAnswers);
      if (nextQ && !updatedAnswers[nextQ.id]) {
        // New question returned
        const newHistory = [...questionHistory.slice(0, currentQuestionIndex + 1), nextQ];
        setQuestionHistory(newHistory);
        setCurrentQuestionIndex(newHistory.length - 1);
        setActiveQuestion(nextQ);
        setCurrentSelectedAnswer(null);
      } else {
        // No more adaptive questions
        moveToWarningSigns();
      }
    } catch (err) {
      console.warn("Error fetching next question", err);
      moveToWarningSigns();
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      const prevIdx = currentQuestionIndex - 1;
      const prevQ = questionHistory[prevIdx];
      setCurrentQuestionIndex(prevIdx);
      setActiveQuestion(prevQ);
      setCurrentSelectedAnswer(answeredQuestions[prevQ.id] ?? null);
    } else {
      setStep(3); // Go back to duration step
    }
  };

  const moveToWarningSigns = () => {
    // Generate context-relevant warning signs for this symptom
    const defaultSigns = [
      "Chest pressure radiating to arm or jaw",
      "Severe shortness of breath at rest",
      "Sudden confusion or slurred speech",
      "Fainting or loss of consciousness",
      "Coughing up blood or vomiting blood",
      "High fever with stiff neck and rash"
    ];
    setAvailableWarningSigns(defaultSigns);
    setStep(5);
  };

  const toggleWarningSign = (sign: string) => {
    if (selectedWarningSigns.includes(sign)) {
      setSelectedWarningSigns(selectedWarningSigns.filter((s) => s !== sign));
    } else {
      setSelectedWarningSigns([...selectedWarningSigns, sign]);
    }
  };

  // Final Step: Evaluate & Complete Assessment
  const handleCompleteAssessment = async () => {
    setLoading(true);
    try {
      const patient = await AsyncStorageWrapper.getPatientProfile();

      const assessmentInput: TriageAssessmentInput = {
        patient_age: patient ? patient.age : 35,
        patient_gender: patient ? patient.gender : "other",
        chief_symptom: selectedSymptom,
        pain_severity: painLevel,
        duration_hours: durationHours,
        progression: progression as any,
        warning_signs: selectedWarningSigns,
        vital_signs: {},
        medical_history: patient ? patient.medical_conditions : [],
        answers: answeredQuestions
      };

      const result: AssessmentResult = await apiClient.evaluateAssessment(assessmentInput);

      // Save to local device history
      await AsyncStorageWrapper.addAssessmentResult(result);

      // Navigate to Results Screen
      navigation.replace("Results", { result });
    } catch (err: any) {
      Alert.alert("Assessment Error", err.message || "Failed to evaluate clinical assessment.");
    } finally {
      setLoading(false);
    }
  };

  // Filter symptoms based on search
  const filteredSymptoms = searchQuery.trim()
    ? allSymptoms.filter((s) =>
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  return (
    <View style={styles.container}>
      {/* Header bar */}
      <View style={styles.topBar}>
        <TouchableOpacity
          onPress={() => {
            if (step > 1) setStep(step - 1);
            else navigation.goBack();
          }}
          style={styles.backBtn}
        >
          <Text style={styles.backBtnText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.topBarTitle}>Symptom Assessment</Text>
        <Text style={styles.stepBadge}>Step {step} of 5</Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* STEP 1: CHIEF SYMPTOM SELECTION */}
        {step === 1 && (
          <View>
            <Text style={styles.stepTitle}>What is your main symptom?</Text>
            <Text style={styles.stepSub}>Select the primary health concern you are experiencing today.</Text>

            <View style={styles.searchBox}>
              <Text style={styles.searchIcon}>🔍</Text>
              <TextInput
                style={styles.searchInput}
                placeholder="Search symptoms (e.g. fever, chest pain)..."
                placeholderTextColor={Colors.textMuted}
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => setSearchQuery("")}>
                  <Text style={styles.clearText}>✕</Text>
                </TouchableOpacity>
              )}
            </View>

            {searchQuery.trim() ? (
              <View style={styles.resultsList}>
                {filteredSymptoms.map((s) => (
                  <TouchableOpacity
                    key={s.id}
                    style={[
                      styles.symptomCard,
                      selectedSymptom === s.id && styles.symptomCardSelected
                    ]}
                    onPress={() => handleSelectSymptom(s.id)}
                  >
                    <Text
                      style={[
                        styles.symptomName,
                        selectedSymptom === s.id && styles.symptomNameSelected
                      ]}
                    >
                      {s.name}
                    </Text>
                    <Text style={styles.symptomCategory}>{s.category}</Text>
                  </TouchableOpacity>
                ))}
                {filteredSymptoms.length === 0 && (
                  <Text style={styles.noResultsText}>No matching symptoms found.</Text>
                )}
              </View>
            ) : (
              <View>
                <Text style={styles.groupHeader}>Common Symptoms</Text>
                <View style={styles.grid}>
                  {COMMON_SYMPTOMS.map((s) => (
                    <TouchableOpacity
                      key={s.id}
                      style={[
                        styles.symptomTile,
                        selectedSymptom === s.id && styles.symptomTileSelected
                      ]}
                      onPress={() => handleSelectSymptom(s.id)}
                    >
                      <Text
                        style={[
                          styles.tileName,
                          selectedSymptom === s.id && styles.tileNameSelected
                        ]}
                      >
                        {s.name}
                      </Text>
                      <Text style={styles.tileCategory}>{s.category}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}
          </View>
        )}

        {/* STEP 2: PAIN LEVEL SELECTION */}
        {step === 2 && (
          <View>
            <Text style={styles.stepTitle}>How severe is your discomfort?</Text>
            <Text style={styles.stepSub}>
              Selected: <Text style={{ fontWeight: "bold" }}>{selectedSymptom.replace(/_/g, " ")}</Text>
            </Text>

            <PainSlider value={painLevel} onChange={setPainLevel} />

            <Button
              title="Next: Duration & Progression →"
              onPress={handleConfirmPain}
              size="large"
              style={styles.nextBtn}
            />
          </View>
        )}

        {/* STEP 3: DURATION & PROGRESSION */}
        {step === 3 && (
          <View>
            <Text style={styles.stepTitle}>Duration and Progression</Text>
            <Text style={styles.stepSub}>How long have you had this symptom and is it changing?</Text>

            <Card style={styles.optionSectionCard}>
              <Text style={styles.sectionHeading}>How long has this been occurring?</Text>
              {DURATION_OPTIONS.map((opt) => {
                const isSelected = durationHours === opt.value;
                return (
                  <TouchableOpacity
                    key={opt.value}
                    style={[styles.selectOption, isSelected && styles.selectOptionActive]}
                    onPress={() => setDurationHours(opt.value)}
                  >
                    <View style={[styles.radioDot, isSelected && styles.radioDotActive]} />
                    <Text style={[styles.selectText, isSelected && styles.selectTextActive]}>
                      {opt.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </Card>

            <Card style={styles.optionSectionCard}>
              <Text style={styles.sectionHeading}>Is the symptom getting better or worse?</Text>
              {PROGRESSION_OPTIONS.map((prog) => {
                const isSelected = progression === prog.value;
                return (
                  <TouchableOpacity
                    key={prog.value}
                    style={[styles.selectOption, isSelected && styles.selectOptionActive]}
                    onPress={() => setProgression(prog.value)}
                  >
                    <View style={[styles.radioDot, isSelected && styles.radioDotActive]} />
                    <Text style={[styles.selectText, isSelected && styles.selectTextActive]}>
                      {prog.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </Card>

            <Button
              title={loading ? "Analyzing..." : "Next: Clinical Questions →"}
              onPress={handleStartAdaptiveQuestions}
              loading={loading}
              size="large"
              style={styles.nextBtn}
            />
          </View>
        )}

        {/* STEP 4: ADAPTIVE QUESTIONS (1 AT A TIME, <= 7 WORDS) */}
        {step === 4 && activeQuestion && (
          <View>
            <ProgressBar
              currentStep={currentQuestionIndex + 1}
              totalSteps={Math.max(currentQuestionIndex + 2, 4)}
              label={`Question ${currentQuestionIndex + 1}`}
            />

            <QuestionCard
              questionId={activeQuestion.id}
              prompt={activeQuestion.prompt}
              subPrompt="Select the most accurate response below:"
              options={activeQuestion.options.map((opt) => ({
                id: opt.value,
                label: opt.label
              }))}
              selectedOptionId={currentSelectedAnswer}
              onSelectOption={(val) => setCurrentSelectedAnswer(val)}
            />

            <View style={styles.btnRow}>
              <Button
                title="← Back"
                onPress={handlePreviousQuestion}
                variant="outline"
                style={styles.halfBtn}
              />
              <Button
                title={loading ? "Checking..." : "Continue →"}
                onPress={handleAnswerQuestion}
                loading={loading}
                style={styles.halfBtn}
              />
            </View>
          </View>
        )}

        {/* STEP 5: WARNING SIGNS CHECK */}
        {step === 5 && (
          <View>
            <Text style={styles.stepTitle}>Critical Warning Signs</Text>
            <Text style={styles.stepSub}>
              Do you have ANY of the following urgent danger signs right now?
            </Text>

            <Card style={styles.warningSignsCard} variant="warning">
              {availableWarningSigns.map((sign, idx) => {
                const isChecked = selectedWarningSigns.includes(sign);
                return (
                  <TouchableOpacity
                    key={`ws-${idx}`}
                    style={[styles.warningItem, isChecked && styles.warningItemActive]}
                    onPress={() => toggleWarningSign(sign)}
                  >
                    <View style={[styles.checkbox, isChecked && styles.checkboxActive]}>
                      {isChecked && <Text style={styles.checkMark}>✓</Text>}
                    </View>
                    <Text style={[styles.warningText, isChecked && styles.warningTextActive]}>
                      {sign}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </Card>

            <Button
              title={loading ? "Evaluating Triage..." : "Complete Clinical Triage →"}
              onPress={handleCompleteAssessment}
              loading={loading}
              size="large"
              variant={selectedWarningSigns.length > 0 ? "emergency" : "primary"}
              style={styles.nextBtn}
            />
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: Spacing.md,
    paddingTop: 44,
    paddingBottom: 12,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border
  },
  backBtn: {
    padding: Spacing.xs
  },
  backBtnText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.blueAccent
  },
  topBarTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  stepBadge: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted
  },
  scrollContent: {
    padding: Spacing.lg,
    paddingBottom: 40
  },
  stepTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    lineHeight: 24,
    marginBottom: 4
  },
  stepSub: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginBottom: Spacing.md
  },
  searchBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: Spacing.inputRadius,
    paddingHorizontal: Spacing.md,
    height: 48,
    marginBottom: Spacing.md
  },
  searchIcon: {
    fontSize: 16,
    marginRight: Spacing.sm
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary
  },
  clearText: {
    fontSize: 16,
    color: Colors.textMuted,
    padding: 4
  },
  resultsList: {
    gap: 8
  },
  symptomCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: Spacing.cardRadius,
    borderWidth: 1.5,
    borderColor: Colors.border
  },
  symptomCardSelected: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  symptomName: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  symptomNameSelected: {
    color: Colors.blueAccent
  },
  symptomCategory: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 2
  },
  noResultsText: {
    textAlign: "center",
    color: Colors.textMuted,
    marginTop: Spacing.lg,
    fontSize: Typography.fontSize.sm
  },
  groupHeader: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: Spacing.sm
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  symptomTile: {
    width: "48%",
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: Spacing.cardRadius,
    borderWidth: 1.5,
    borderColor: Colors.border
  },
  symptomTileSelected: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  tileName: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  tileNameSelected: {
    color: Colors.blueAccent
  },
  tileCategory: {
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 4
  },
  optionSectionCard: {
    padding: Spacing.md,
    marginBottom: Spacing.md
  },
  sectionHeading: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    marginBottom: Spacing.sm
  },
  selectOption: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.sm,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: 6,
    backgroundColor: Colors.surface
  },
  selectOptionActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  radioDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: Colors.border,
    marginRight: Spacing.sm
  },
  radioDotActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueAccent
  },
  selectText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textPrimary
  },
  selectTextActive: {
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  btnRow: {
    flexDirection: "row",
    gap: Spacing.sm,
    marginTop: Spacing.md
  },
  halfBtn: {
    flex: 1
  },
  nextBtn: {
    marginTop: Spacing.lg
  },
  warningSignsCard: {
    padding: Spacing.md,
    marginBottom: Spacing.md
  },
  warningItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.sm,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: 8,
    backgroundColor: Colors.surface
  },
  warningItemActive: {
    borderColor: Colors.emergency,
    backgroundColor: Colors.dangerTint
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 1.5,
    borderColor: Colors.border,
    justifyContent: "center",
    alignItems: "center",
    marginRight: Spacing.sm
  },
  checkboxActive: {
    borderColor: Colors.emergency,
    backgroundColor: Colors.emergency
  },
  checkMark: {
    color: Colors.white,
    fontSize: 12,
    fontWeight: "bold"
  },
  warningText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textPrimary,
    flex: 1,
    lineHeight: 18
  },
  warningTextActive: {
    fontWeight: Typography.fontWeight.bold,
    color: Colors.emergency
  }
});
