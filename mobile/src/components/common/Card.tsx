import React from "react";
import { View, StyleSheet, ViewStyle } from "react-native";
import { Colors } from "../../theme/colors";
import { Spacing } from "../../theme/spacing";

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: "default" | "elevated" | "accent" | "emergency" | "warning";
}

export const Card: React.FC<CardProps> = ({ children, style, variant = "default" }) => {
  const getVariantStyle = () => {
    switch (variant) {
      case "elevated":
        return styles.elevated;
      case "accent":
        return styles.accent;
      case "emergency":
        return styles.emergency;
      case "warning":
        return styles.warning;
      default:
        return styles.default;
    }
  };

  return <View style={[styles.base, getVariantStyle(), style]}>{children}</View>;
};

const styles = StyleSheet.create({
  base: {
    backgroundColor: Colors.surface,
    borderRadius: Spacing.cardRadius,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md
  },
  default: {},
  elevated: {
    shadowColor: Colors.navyPrimary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2
  },
  accent: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  emergency: {
    borderColor: Colors.urgentEmergency,
    backgroundColor: Colors.urgentEmergencyBg
  },
  warning: {
    borderColor: Colors.urgentEarly,
    backgroundColor: Colors.urgentEarlyBg
  }
});
