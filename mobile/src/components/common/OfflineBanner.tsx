import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface OfflineBannerProps {
  isOffline: boolean;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({ isOffline }) => {
  if (!isOffline) return null;

  return (
    <View style={styles.banner}>
      <Text style={styles.icon}>⚡</Text>
      <Text style={styles.text}>
        Offline Mode Active — Using 100% local clinical triage & Maharashtra hospital cache
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  banner: {
    backgroundColor: "#FEF3C7",
    borderBottomWidth: 1,
    borderColor: "#F59E0B",
    paddingVertical: Spacing.xs + 2,
    paddingHorizontal: Spacing.md,
    flexDirection: "row",
    alignItems: "center"
  },
  icon: {
    fontSize: 14,
    marginRight: Spacing.sm
  },
  text: {
    ...Typography.small,
    color: "#92400E",
    fontWeight: "600",
    flex: 1
  }
});
