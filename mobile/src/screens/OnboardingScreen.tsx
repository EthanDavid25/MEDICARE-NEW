import React from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Button } from "../components/common/Button";
import { Card } from "../components/common/Card";

interface OnboardingScreenProps {
  navigation: any;
}

export const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.appTitle}>MEDICARE</Text>
          <Text style={styles.heading}>Clinical Triage & Decision Support</Text>
          <Text style={styles.subheading}>
            Evidence-based medical urgency assessment designed for Maharashtra, India.
          </Text>
        </View>

        <Card style={styles.featureCard} variant="elevated">
          <Text style={styles.cardHeader}>Key Features</Text>

          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>⚡</Text>
            <View style={styles.featureTextContainer}>
              <Text style={styles.featureTitle}>Adaptive Symptom Assessment</Text>
              <Text style={styles.featureDesc}>
                Concise questions (≤ 7 words) dynamically tailored to your chief symptoms.
              </Text>
            </View>
          </View>

          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>🛡️</Text>
            <View style={styles.featureTextContainer}>
              <Text style={styles.featureTitle}>100% Offline Capability</Text>
              <Text style={styles.featureDesc}>
                Full clinical triage engine runs locally without requiring Wi-Fi or mobile data.
              </Text>
            </View>
          </View>

          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>🏥</Text>
            <View style={styles.featureTextContainer}>
              <Text style={styles.featureTitle}>Verified Maharashtra Directory</Text>
              <Text style={styles.featureDesc}>
                Direct access to 14 tertiary emergency facilities across Mumbai, Pune, Thane & beyond.
              </Text>
            </View>
          </View>

          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>📋</Text>
            <View style={styles.featureTextContainer}>
              <Text style={styles.featureTitle}>Doctor Handover Reports</Text>
              <Text style={styles.featureDesc}>
                Professional clinical summaries ready to share with attending physicians.
              </Text>
            </View>
          </View>
        </Card>

        <Card style={styles.disclaimerCard} variant="emergency">
          <Text style={styles.disclaimerTitle}>⚠️ Emergency Notice & Limitations</Text>
          <Text style={styles.disclaimerText}>
            MEDICARE is a clinical triage and decision support tool for informational guidance. It does not replace professional medical evaluation, diagnosis or physician advice.
          </Text>
          <Text style={[styles.disclaimerText, { marginTop: 8, fontWeight: "bold" }]}>
            If you or someone around you experiences severe chest pain, difficulty breathing, loss of consciousness, or severe trauma, call 112 or 108 immediately.
          </Text>
        </Card>
      </ScrollView>

      <View style={styles.footer}>
        <Button
          title="Agree & Get Started"
          onPress={() => navigation.navigate("Registration")}
          fullWidth
          size="large"
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background
  },
  scrollContent: {
    padding: Spacing.lg,
    paddingTop: 50,
    paddingBottom: 20
  },
  header: {
    marginBottom: Spacing.lg
  },
  appTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.blueAccent,
    letterSpacing: 1.5,
    marginBottom: 4
  },
  heading: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    lineHeight: 28,
    marginBottom: 6
  },
  subheading: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    lineHeight: 20
  },
  featureCard: {
    padding: Spacing.lg,
    marginBottom: Spacing.lg
  },
  cardHeader: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    marginBottom: Spacing.md
  },
  featureRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: Spacing.md
  },
  featureIcon: {
    fontSize: 22,
    marginRight: Spacing.md,
    marginTop: 2
  },
  featureTextContainer: {
    flex: 1
  },
  featureTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.navyPrimary,
    marginBottom: 2
  },
  featureDesc: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    lineHeight: 18
  },
  disclaimerCard: {
    backgroundColor: Colors.dangerTint,
    borderColor: "#FECACA",
    marginBottom: Spacing.lg
  },
  disclaimerTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.emergency,
    marginBottom: Spacing.xs
  },
  disclaimerText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textPrimary,
    lineHeight: 18
  },
  footer: {
    padding: Spacing.lg,
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight
  }
});
