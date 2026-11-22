import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

export interface QuestionOption {
  id: string | number | boolean;
  label: string;
  sublabel?: string;
}

interface QuestionCardProps {
  questionId: string;
  prompt: string;
  subPrompt?: string;
  options: QuestionOption[];
  selectedOptionId?: string | number | boolean | null;
  onSelectOption: (optionId: any) => void;
  disabled?: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  questionId,
  prompt,
  subPrompt,
  options,
  selectedOptionId,
  onSelectOption,
  disabled = false
}) => {
  return (
    <View style={styles.card}>
      <Text style={styles.promptText}>{prompt}</Text>
      {subPrompt ? <Text style={styles.subPromptText}>{subPrompt}</Text> : null}

      <View style={styles.optionsList}>
        {options.map((opt, idx) => {
          const isSelected = selectedOptionId === opt.id;
          return (
            <TouchableOpacity
              key={`${questionId}-opt-${idx}`}
              style={[
                styles.optionItem,
                isSelected && styles.optionItemSelected,
                disabled && styles.optionDisabled
              ]}
              onPress={() => !disabled && onSelectOption(opt.id)}
              activeOpacity={0.7}
              disabled={disabled}
            >
              <View style={[styles.radioCircle, isSelected && styles.radioCircleSelected]}>
                {isSelected && <View style={styles.radioInnerCircle} />}
              </View>
              <View style={styles.optionContent}>
                <Text
                  style={[
                    styles.optionLabel,
                    isSelected && styles.optionLabelSelected
                  ]}
                >
                  {opt.label}
                </Text>
                {opt.sublabel ? (
                  <Text style={styles.optionSublabel}>{opt.sublabel}</Text>
                ) : null}
              </View>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: Spacing.cardRadius,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: Colors.navyPrimary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
    marginBottom: Spacing.md
  },
  promptText: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    lineHeight: 24,
    marginBottom: Spacing.xs
  },
  subPromptText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    marginBottom: Spacing.md
  },
  optionsList: {
    marginTop: Spacing.sm
  },
  optionItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.md,
    borderRadius: Spacing.buttonRadius,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
    marginBottom: Spacing.sm,
    minHeight: 52
  },
  optionItemSelected: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  optionDisabled: {
    opacity: 0.6
  },
  radioCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: Colors.border,
    justifyContent: "center",
    alignItems: "center",
    marginRight: Spacing.md
  },
  radioCircleSelected: {
    borderColor: Colors.blueAccent
  },
  radioInnerCircle: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Colors.blueAccent
  },
  optionContent: {
    flex: 1
  },
  optionLabel: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.textPrimary
  },
  optionLabelSelected: {
    color: Colors.navyPrimary,
    fontWeight: Typography.fontWeight.semiBold
  },
  optionSublabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 2
  }
});
