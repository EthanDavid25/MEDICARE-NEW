import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface BadgeProps {
  label: string;
  category?: 1 | 2 | 3 | 4;
  color?: string;
  bgColor?: string;
}

export const Badge: React.FC<BadgeProps> = ({ label, category, color, bgColor }) => {
  let badgeColor = color || Colors.blueAccent;
  let badgeBg = bgColor || Colors.blueTint;

  if (category === 1) {
    badgeColor = Colors.urgentEmergency;
    badgeBg = Colors.urgentEmergencyBg;
  } else if (category === 2) {
    badgeColor = Colors.urgentEarly;
    badgeBg = Colors.urgentEarlyBg;
  } else if (category === 3) {
    badgeColor = Colors.urgentRoutine;
    badgeBg = Colors.urgentRoutineBg;
  } else if (category === 4) {
    badgeColor = Colors.urgentInsuff;
    badgeBg = Colors.urgentInsuffBg;
  }

  return (
    <View style={[styles.badge, { backgroundColor: badgeBg, borderColor: badgeColor }]}>
      <Text style={[styles.text, { color: badgeColor }]}>{label}</Text>
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
  text: {
    ...Typography.small,
    fontWeight: "700",
    textTransform: "uppercase"
  }
});
