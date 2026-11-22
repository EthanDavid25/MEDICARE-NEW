import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  label?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentStep,
  totalSteps,
  label
}) => {
  const percentage = Math.min(100, Math.max(0, totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0));

  return (
    <View style={styles.container}>
      <View style={styles.textRow}>
        <Text style={styles.stepText}>
          {label ? label : `Question ${currentStep} of ${totalSteps}`}
        </Text>
        <Text style={styles.percentText}>{Math.round(percentage)}%</Text>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${percentage}%` }]} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: Spacing.sm
  },
  textRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.xs
  },
  stepText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.textMuted
  },
  percentText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.navyPrimary
  },
  track: {
    height: 6,
    backgroundColor: Colors.border,
    borderRadius: 3,
    overflow: "hidden"
  },
  fill: {
    height: "100%",
    backgroundColor: Colors.blueAccent,
    borderRadius: 3
  }
});
