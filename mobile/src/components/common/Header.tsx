import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, StatusBar } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface HeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  showBack = false,
  onBack,
  rightAction
}) => {
  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.navyPrimary} />
      <View style={styles.row}>
        {showBack ? (
          <TouchableOpacity onPress={onBack} style={styles.backButton} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.brandRow}>
            <View style={styles.logoBadge}>
              <Text style={styles.logoText}>M</Text>
            </View>
            <Text style={styles.brandTitle}>MEDICARE</Text>
          </View>
        )}
        {rightAction && <View style={styles.rightAction}>{rightAction}</View>}
      </View>
      <View style={styles.titleSection}>
        <Text style={styles.pageTitle}>{title}</Text>
        {subtitle ? <Text style={styles.pageSubtitle}>{subtitle}</Text> : null}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.navyPrimary,
    paddingTop: StatusBar.currentHeight ? StatusBar.currentHeight + 8 : 40,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.md
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: Spacing.sm
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center"
  },
  logoBadge: {
    width: 24,
    height: 24,
    borderRadius: 6,
    backgroundColor: Colors.blueAccent,
    alignItems: "center",
    justifyContent: "center",
    marginRight: Spacing.sm
  },
  logoText: {
    color: Colors.textLight,
    fontWeight: "800",
    fontSize: 14
  },
  brandTitle: {
    ...Typography.body1,
    color: Colors.textLight,
    fontWeight: "700",
    letterSpacing: 0.5
  },
  backButton: {
    paddingVertical: Spacing.xs
  },
  backText: {
    ...Typography.body2,
    color: Colors.blueLight,
    fontWeight: "600"
  },
  rightAction: {
    marginLeft: "auto"
  },
  titleSection: {
    marginTop: Spacing.xs
  },
  pageTitle: {
    ...Typography.h2,
    color: Colors.textLight
  },
  pageSubtitle: {
    ...Typography.caption,
    color: Colors.textMuted,
    marginTop: 2
  }
});
