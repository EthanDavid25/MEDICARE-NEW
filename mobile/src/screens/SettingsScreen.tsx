import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";
import { AsyncStorageWrapper } from "../storage/asyncStorage";
import { apiClient } from "../api/client";
import { PatientProfile } from "../../shared/types";

interface SettingsScreenProps {
  navigation: any;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ navigation }) => {
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [offlinePreferred, setOfflinePreferred] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const p = await AsyncStorageWrapper.getPatientProfile();
      setProfile(p);

      const online = await apiClient.isBackendOnline();
      setIsBackendOnline(online);
    } catch (err) {
      console.warn("Failed to load settings", err);
    }
  };

  const handleResetProfile = () => {
    Alert.alert(
      "Reset Profile",
      "Are you sure you want to re-register your profile? Current patient details will be overwritten.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Reset",
          style: "destructive",
          onPress: () => {
            navigation.navigate("Registration");
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings & System</Text>
        <Text style={styles.headerSubtitle}>MEDICARE Offline-First Health Engine</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* PATIENT PROFILE CARD */}
        <Card style={styles.sectionCard}>
          <View style={styles.cardHeaderRow}>
            <Text style={styles.sectionTitle}>Registered Patient Profile</Text>
            <TouchableOpacity onPress={() => navigation.navigate("Registration")}>
              <Text style={styles.editLink}>Edit</Text>
            </TouchableOpacity>
          </View>

          {profile ? (
            <View style={styles.profileBox}>
              <View style={styles.profileRow}>
                <Text style={styles.profileName}>{profile.name}</Text>
                <Badge text={`${profile.age} yrs • ${profile.gender.toUpperCase()}`} variant="info" size="small" />
              </View>
              <Text style={styles.profileMeta}>📱 {profile.phone}</Text>
              {profile.emergency_contact ? (
                <Text style={styles.profileMeta}>🚨 Emergency Contact: {profile.emergency_contact}</Text>
              ) : null}
              <Text style={styles.profileMeta}>🩸 Blood Group: {profile.blood_group || "Not specified"}</Text>
              {profile.medical_conditions?.length ? (
                <Text style={styles.profileMeta}>
                  🏥 Chronic Conditions: {profile.medical_conditions.join(", ")}
                </Text>
              ) : null}
            </View>
          ) : (
            <TouchableOpacity onPress={() => navigation.navigate("Registration")}>
              <Text style={styles.noProfileText}>No profile found. Tap to set up profile.</Text>
            </TouchableOpacity>
          )}
        </Card>

        {/* CLINICAL DATASET STATUS */}
        <Card style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Offline Medical Datasets</Text>
          <Text style={styles.sectionDesc}>
            All clinical knowledge is bundled directly into the mobile binary for autonomous operation without network connectivity.
          </Text>

          <View style={styles.datasetList}>
            <View style={styles.datasetRow}>
              <Text style={styles.datasetLabel}>Symptom Dictionary</Text>
              <Text style={styles.datasetVal}>81 Verified Symptoms</Text>
            </View>
            <View style={styles.datasetRow}>
              <Text style={styles.datasetLabel}>Adaptive Questions</Text>
              <Text style={styles.datasetVal}>28 Clinical Questions (≤7 words)</Text>
            </View>
            <View style={styles.datasetRow}>
              <Text style={styles.datasetLabel}>Triage Inference Rules</Text>
              <Text style={styles.datasetVal}>22 Evaluated Rules</Text>
            </View>
            <View style={styles.datasetRow}>
              <Text style={styles.datasetLabel}>Urgent Warning Signs</Text>
              <Text style={styles.datasetVal}>40 Danger Indicators</Text>
            </View>
            <View style={styles.datasetRow}>
              <Text style={styles.datasetLabel}>Maharashtra Facilities</Text>
              <Text style={styles.datasetVal}>14 Verified Hospitals</Text>
            </View>
          </View>
        </Card>

        {/* BACKEND CONNECTIVITY */}
        <Card style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Backend Synchronization</Text>
          <View style={styles.syncRow}>
            <View style={styles.syncStatusLeft}>
              <View
                style={[
                  styles.statusDot,
                  { backgroundColor: isBackendOnline ? Colors.selfCare : Colors.emergency }
                ]}
              />
              <Text style={styles.syncStatusText}>
                {isBackendOnline ? "Connected to Backend API" : "Operating in Standalone Offline Mode"}
              </Text>
            </View>
            <Badge
              text={isBackendOnline ? "ONLINE" : "OFFLINE"}
              variant={isBackendOnline ? "success" : "neutral"}
              size="small"
            />
          </View>
          <Text style={styles.syncHint}>
            When offline, the TypeScript clinical equivalence engine provides 100% authoritative triage results locally.
          </Text>
        </Card>

        {/* APP INFO & DISCLAIMER */}
        <Card style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>About MEDICARE Mobile</Text>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Application Version</Text>
            <Text style={styles.aboutValue}>1.0.0 (Build 202611)</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Clinical Engine Version</Text>
            <Text style={styles.aboutValue}>v2.1.0 (Compact Adaptive)</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Jurisdiction Target</Text>
            <Text style={styles.aboutValue}>Maharashtra, India</Text>
          </View>

          <Text style={styles.disclaimerText}>
            MEDICARE is a clinical triage and decision support system. It is designed to assist in determining the urgency of medical evaluation and is not a substitute for professional clinical diagnosis.
          </Text>
        </Card>

        {/* RESET BUTTON */}
        <TouchableOpacity style={styles.resetBtn} onPress={handleResetProfile}>
          <Text style={styles.resetBtnText}>Re-register / Reset Profile</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background
  },
  header: {
    paddingTop: 50,
    paddingBottom: 14,
    paddingHorizontal: Spacing.md,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border
  },
  headerTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  headerSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginTop: 2
  },
  scrollContent: {
    padding: Spacing.md,
    paddingBottom: 40
  },
  sectionCard: {
    padding: Spacing.md,
    marginBottom: Spacing.md
  },
  cardHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.sm
  },
  sectionTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: Spacing.xs
  },
  sectionDesc: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
    lineHeight: 18
  },
  editLink: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.blueAccent
  },
  profileBox: {
    backgroundColor: Colors.surfaceAlt,
    padding: Spacing.md,
    borderRadius: 8
  },
  profileRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.xs
  },
  profileName: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  profileMeta: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginTop: 3
  },
  noProfileText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.blueAccent,
    fontWeight: Typography.fontWeight.medium,
    paddingVertical: Spacing.sm
  },
  datasetList: {
    marginTop: Spacing.xs
  },
  datasetRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight
  },
  datasetLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textPrimary
  },
  datasetVal: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  syncRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: Spacing.xs
  },
  syncStatusLeft: {
    flexDirection: "row",
    alignItems: "center"
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8
  },
  syncStatusText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.textPrimary
  },
  syncHint: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 4,
    lineHeight: 16
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 4
  },
  aboutLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary
  },
  aboutValue: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  disclaimerText: {
    fontSize: 10,
    color: Colors.textMuted,
    lineHeight: 16,
    marginTop: Spacing.md,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight
  },
  resetBtn: {
    alignItems: "center",
    paddingVertical: Spacing.md
  },
  resetBtnText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.emergency
  }
});
