import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

export interface BadgeProps {
  label?: string;
  text?: string;
  category?: 1 | 2 | 3 | 4;
  variant?: "danger" | "warning" | "info" | "success" | "neutral" | string;
  size?: "small" | "medium" | "large";
  color?: string;
  bgColor?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  text,
  category,
  variant,
  size = "medium",
  color,
  bgColor
}) => {
  const displayLabel = label || text || "";
  let badgeColor = color || Colors.blueAccent;
  let badgeBg = bgColor || Colors.blueTint;

  if (category === 1 || variant === "danger") {
    badgeColor = Colors.urgentEmergency;
    badgeBg = Colors.urgentEmergencyBg;
  } else if (category === 2 || variant === "warning") {
    badgeColor = Colors.urgentEarly;
    badgeBg = Colors.urgentEarlyBg;
  } else if (category === 3 || variant === "success") {
    badgeColor = Colors.urgentRoutine;
    badgeBg = Colors.urgentRoutineBg;
  } else if (category === 4 || variant === "neutral") {
    badgeColor = Colors.urgentInsuff;
    badgeBg = Colors.urgentInsuffBg;
  } else if (variant === "info") {
    badgeColor = Colors.blueAccent;
    badgeBg = Colors.blueTint;
  }

  const isSmall = size === "small";

  return (
    <View
      style={[
        styles.badge,
        isSmall && styles.badgeSmall,
        { backgroundColor: badgeBg, borderColor: badgeColor }
      ]}
    >
      <Text style={[styles.text, isSmall && styles.textSmall, { color: badgeColor }]}>
        {displayLabel}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    alignSelf: "flex-start"
  },
  badgeSmall: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  text: {
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase"
  },
  textSmall: {
    fontSize: 9,
    fontWeight: "700"
  }
});
