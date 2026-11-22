import React, { useEffect } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { AsyncStorageWrapper } from "../storage/asyncStorage";

interface SplashScreenProps {
  navigation: any;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ navigation }) => {
  useEffect(() => {
    const checkInit = async () => {
      try {
        await new Promise((r) => setTimeout(r, 1200)); // Smooth splash presentation
        const profile = await AsyncStorageWrapper.getPatientProfile();
        if (profile && profile.phone) {
          navigation.replace("MainTabs");
        } else {
          navigation.replace("Onboarding");
        }
      } catch (err) {
        navigation.replace("Onboarding");
      }
    };

    checkInit();
  }, [navigation]);

  return (
    <View style={styles.container}>
      <View style={styles.brandBox}>
        <View style={styles.crossCircle}>
          <Text style={styles.crossSymbol}>✚</Text>
        </View>
        <Text style={styles.title}>MEDICARE</Text>
        <Text style={styles.tagline}>Intelligent Medical Triage</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>OFFLINE-FIRST CLINICAL ENGINE</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <ActivityIndicator size="small" color={Colors.white} />
        <Text style={styles.footerText}>Maharashtra Healthcare Edition • v1.0.0</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.navyPrimary,
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 60,
    paddingHorizontal: Spacing.lg
  },
  brandBox: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center"
  },
  crossCircle: {
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: Colors.white,
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 4,
    marginBottom: Spacing.md
  },
  crossSymbol: {
    fontSize: 44,
    color: Colors.emergency,
    fontWeight: "bold",
    marginTop: -2
  },
  title: {
    fontSize: Typography.fontSize.xxl + 4,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.white,
    letterSpacing: 2
  },
  tagline: {
    fontSize: Typography.fontSize.md,
    color: "#93C5FD",
    marginTop: 6,
    letterSpacing: 0.5
  },
  badge: {
    backgroundColor: "rgba(255, 255, 255, 0.12)",
    paddingHorizontal: Spacing.md,
    paddingVertical: 5,
    borderRadius: 16,
    marginTop: Spacing.lg,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.2)"
  },
  badgeText: {
    fontSize: 10,
    color: Colors.white,
    fontWeight: Typography.fontWeight.semiBold,
    letterSpacing: 1
  },
  footer: {
    alignItems: "center",
    gap: Spacing.sm
  },
  footerText: {
    fontSize: Typography.fontSize.xs,
    color: "rgba(255, 255, 255, 0.6)"
  }
});
