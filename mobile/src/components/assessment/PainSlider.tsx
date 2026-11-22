import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface PainSliderProps {
  value: number;
  onChange: (val: number) => void;
}

export const PainSlider: React.FC<PainSliderProps> = ({ value, onChange }) => {
  const getDescriptor = (score: number) => {
    if (score === 0) return { label: "No Pain", color: Colors.urgentRoutine };
    if (score <= 3) return { label: "Mild Discomfort", color: Colors.urgentRoutine };
    if (score <= 6) return { label: "Moderate Pain", color: Colors.urgentEarly };
    if (score <= 8) return { label: "Severe Pain", color: "#EA580C" };
    return { label: "Worst Possible Pain (Emergency Flag)", color: Colors.urgentEmergency };
  };

  const current = getDescriptor(value);

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>Pain & Severity Intensity</Text>
        <View style={[styles.scoreBadge, { backgroundColor: current.color }]}>
          <Text style={styles.scoreText}>{value} / 10</Text>
        </View>
      </View>
      <Text style={[styles.descriptor, { color: current.color }]}>{current.label}</Text>

      {/* Numerical buttons from 0 to 10 */}
      <View style={styles.buttonsRow}>
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => {
          const isSelected = value === num;
          let btnColor = Colors.border;
          if (num === 0) btnColor = Colors.urgentRoutine;
          else if (num <= 3) btnColor = Colors.urgentRoutine;
          else if (num <= 6) btnColor = Colors.urgentEarly;
          else if (num <= 8) btnColor = "#EA580C";
          else btnColor = Colors.urgentEmergency;

          return (
            <TouchableOpacity
              key={num}
              style={[
                styles.numButton,
                isSelected && { backgroundColor: btnColor, borderColor: btnColor }
              ]}
              onPress={() => onChange(num)}
              activeOpacity={0.7}
            >
              <Text style={[styles.numText, isSelected && styles.numTextSelected]}>
                {num}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
      <View style={styles.scaleLabels}>
        <Text style={styles.scaleText}>0 - None</Text>
        <Text style={styles.scaleText}>5 - Moderate</Text>
        <Text style={styles.scaleText}>10 - Unbearable</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: Spacing.cardRadius,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  title: {
    ...Typography.body1,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  scoreBadge: {
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: 3,
    borderRadius: 8
  },
  scoreText: {
    ...Typography.body2,
    color: Colors.textLight,
    fontWeight: "700"
  },
  descriptor: {
    ...Typography.caption,
    fontWeight: "600",
    marginTop: 2,
    marginBottom: Spacing.md
  },
  buttonsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  numButton: {
    width: 28,
    height: 38,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.surfaceSubtle,
    alignItems: "center",
    justifyContent: "center"
  },
  numText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textSecondary
  },
  numTextSelected: {
    color: Colors.textLight,
    fontWeight: "800"
  },
  scaleLabels: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: Spacing.sm
  },
  scaleText: {
    ...Typography.small,
    color: Colors.textMuted
  }
});
