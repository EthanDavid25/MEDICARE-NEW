import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Linking } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface EmergencyCallBannerProps {
  compact?: boolean;
}

export const EmergencyCallBanner: React.FC<EmergencyCallBannerProps> = ({ compact = false }) => {
  const callNumber = (number: string) => {
    Linking.openURL(`tel:${number}`);
  };

  const emergencyServices = [
    { number: "112", label: "National Emergency", sub: "All Emergencies" },
    { number: "108", label: "Ambulance", sub: "Free Emergency Service" },
    { number: "102", label: "Maternity / Child", sub: "Govt Ambulance" },
    { number: "104", label: "Medical Helpline", sub: "24/7 Advice" }
  ];

  if (compact) {
    return (
      <View style={styles.compactContainer}>
        <View style={styles.compactHeader}>
          <Text style={styles.compactIcon}>🚨</Text>
          <Text style={styles.compactTitle}>Emergency Services (India)</Text>
        </View>
        <View style={styles.compactRow}>
          <TouchableOpacity
            style={[styles.compactBtn, styles.btn112]}
            onPress={() => callNumber("112")}
          >
            <Text style={styles.compactBtnText}>📞 112</Text>
            <Text style={styles.compactBtnSub}>All Emergencies</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.compactBtn, styles.btn108]}
            onPress={() => callNumber("108")}
          >
            <Text style={styles.compactBtnText}>🚑 108</Text>
            <Text style={styles.compactBtnSub}>Ambulance</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.headerIcon}>🚨</Text>
        <View>
          <Text style={styles.headerTitle}>Emergency Medical Helplines</Text>
          <Text style={styles.headerSub}>Toll-free 24/7 emergency services across India</Text>
        </View>
      </View>

      <View style={styles.grid}>
        {emergencyServices.map((svc) => (
          <TouchableOpacity
            key={svc.number}
            style={styles.gridItem}
            onPress={() => callNumber(svc.number)}
            activeOpacity={0.8}
          >
            <View style={styles.badge}>
              <Text style={styles.badgeText}>CALL {svc.number}</Text>
            </View>
            <Text style={styles.itemLabel}>{svc.label}</Text>
            <Text style={styles.itemSub}>{svc.sub}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.dangerTint,
    borderRadius: Spacing.cardRadius,
    borderWidth: 1.5,
    borderColor: "#FECACA",
    padding: Spacing.md,
    marginBottom: Spacing.md
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.sm
  },
  headerIcon: {
    fontSize: 22,
    marginRight: Spacing.sm
  },
  headerTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.emergency
  },
  headerSub: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 4
  },
  gridItem: {
    flex: 1,
    minWidth: "46%",
    backgroundColor: Colors.surface,
    borderRadius: Spacing.buttonRadius,
    padding: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: "center"
  },
  badge: {
    backgroundColor: Colors.emergency,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: 6,
    marginBottom: 4
  },
  badgeText: {
    color: Colors.white,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold
  },
  itemLabel: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.navyPrimary
  },
  itemSub: {
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 2
  },
  compactContainer: {
    backgroundColor: Colors.dangerTint,
    borderRadius: Spacing.cardRadius,
    padding: Spacing.sm,
    borderWidth: 1,
    borderColor: "#FECACA",
    marginBottom: Spacing.sm
  },
  compactHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: Spacing.xs
  },
  compactIcon: {
    fontSize: 16,
    marginRight: 6
  },
  compactTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.emergency
  },
  compactRow: {
    flexDirection: "row",
    gap: 8
  },
  compactBtn: {
    flex: 1,
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 6,
    alignItems: "center"
  },
  btn112: {
    backgroundColor: Colors.emergency
  },
  btn108: {
    backgroundColor: "#B91C1C"
  },
  compactBtnText: {
    color: Colors.white,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold
  },
  compactBtnSub: {
    color: Colors.white,
    fontSize: 9,
    opacity: 0.9
  }
});
