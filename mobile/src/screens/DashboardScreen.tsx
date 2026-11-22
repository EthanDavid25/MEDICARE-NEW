import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";
import { Button } from "../components/common/Button";
import { OfflineBanner } from "../components/common/OfflineBanner";
import { EmergencyCallBanner } from "../components/hospitals/EmergencyCallBanner";
import { AsyncStorageWrapper } from "../storage/asyncStorage";
import { apiClient } from "../api/client";
import { PatientProfile, AssessmentResult } from "../types";

interface DashboardScreenProps {
  navigation: any;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({ navigation }) => {
  const [patient, setPatient] = useState<PatientProfile | null>(null);
  const [history, setHistory] = useState<AssessmentResult[]>([]);
  const [isOffline, setIsOffline] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const profile = await AsyncStorageWrapper.getPatientProfile();
      setPatient(profile);

      const pastAssessments = await AsyncStorageWrapper.getAssessmentHistory();
      setHistory(pastAssessments.slice(0, 3));

      const online = await apiClient.isBackendOnline();
      setIsOffline(!online);
    } catch (err) {
      console.warn("Failed to load dashboard data", err);
    }
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener("focus", () => {
      loadData();
    });
    loadData();
    return unsubscribe;
  }, [navigation]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const getUrgencyBadge = (category: string) => {
    switch (category.toLowerCase()) {
      case "emergency":
        return <Badge text="EMERGENCY" variant="danger" size="small" />;
      case "urgent":
        return <Badge text="URGENT" variant="warning" size="small" />;
      case "routine":
        return <Badge text="ROUTINE" variant="info" size="small" />;
      default:
        return <Badge text="SELF-CARE" variant="success" size="small" />;
    }
  };

  return (
    <View style={styles.container}>
      <OfflineBanner isOffline={isOffline} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Welcome Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.patientName}>{patient ? patient.name : "Patient"}</Text>
          </View>
          {patient && (
            <View style={styles.profileBadge}>
              <Text style={styles.profileBadgeText}>
                {patient.age}y • {(patient.gender || "U").charAt(0).toUpperCase()}
              </Text>
            </View>
          )}
        </View>

        {/* Emergency Helplines Quick Access */}
        <EmergencyCallBanner compact />

        {/* Primary Action Card: Start Assessment */}
        <TouchableOpacity
          activeOpacity={0.9}
          onPress={() => navigation.navigate("Assessment")}
        >
          <Card style={styles.startCard} variant="accent">
            <View style={styles.startRow}>
              <View style={styles.startTextCol}>
                <Text style={styles.startBadge}>CLINICAL TRIAGE</Text>
                <Text style={styles.startTitle}>Start New Symptom Assessment</Text>
                <Text style={styles.startDesc}>
                  Evaluates 81 symptoms with adaptive questions (≤ 7 words) & instant urgency classification.
                </Text>
              </View>
              <View style={styles.startIconCircle}>
                <Text style={styles.startIcon}>🩺</Text>
              </View>
            </View>
            <Button
              title="Begin Assessment →"
              onPress={() => navigation.navigate("Assessment")}
              variant="primary"
              size="medium"
              style={styles.startBtn}
            />
          </Card>
        </TouchableOpacity>

        {/* Quick Nav Tiles */}
        <Text style={styles.sectionTitle}>Healthcare Quick Actions</Text>
        <View style={styles.tilesGrid}>
          <TouchableOpacity
            style={styles.tile}
            onPress={() => navigation.navigate("Hospitals")}
            activeOpacity={0.7}
          >
            <Text style={styles.tileIcon}>🏥</Text>
            <Text style={styles.tileTitle}>Hospitals</Text>
            <Text style={styles.tileSubtitle}>14 MH Facilities</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tile}
            onPress={() => navigation.navigate("History")}
            activeOpacity={0.7}
          >
            <Text style={styles.tileIcon}>📑</Text>
            <Text style={styles.tileTitle}>Assessments</Text>
            <Text style={styles.tileSubtitle}>Past Reports</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tile}
            onPress={() => {
              if (history.length > 0) {
                navigation.navigate("DoctorHandover", { result: history[0] });
              } else {
                navigation.navigate("Assessment");
              }
            }}
            activeOpacity={0.7}
          >
            <Text style={styles.tileIcon}>📋</Text>
            <Text style={styles.tileTitle}>Handover</Text>
            <Text style={styles.tileSubtitle}>Doctor Summary</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tile}
            onPress={() => navigation.navigate("Settings")}
            activeOpacity={0.7}
          >
            <Text style={styles.tileIcon}>⚙️</Text>
            <Text style={styles.tileTitle}>Settings</Text>
            <Text style={styles.tileSubtitle}>Offline & Profile</Text>
          </TouchableOpacity>
        </View>

        {/* Recent Assessments Section */}
        <View style={styles.recentSection}>
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>Recent Assessments</Text>
            {history.length > 0 && (
              <TouchableOpacity onPress={() => navigation.navigate("History")}>
                <Text style={styles.seeAllText}>See all ({history.length})</Text>
              </TouchableOpacity>
            )}
          </View>

          {history.length === 0 ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyIcon}>🩺</Text>
              <Text style={styles.emptyTitle}>No Assessments Yet</Text>
              <Text style={styles.emptyDesc}>
                Start an assessment whenever you or a family member experience medical symptoms.
              </Text>
            </Card>
          ) : (
            history.map((item, idx) => (
              <TouchableOpacity
                key={item.assessment_id || `hist-${idx}`}
                onPress={() => navigation.navigate("Results", { result: item })}
                activeOpacity={0.7}
              >
                <Card style={styles.recentCard}>
                  <View style={styles.recentRow}>
                    <View style={styles.recentCol}>
                      <Text style={styles.recentSymptom}>
                        {item.chief_symptom.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                      </Text>
                      <Text style={styles.recentDate}>
                        {new Date(item.timestamp).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short",
                          year: "numeric"
                        })}
                      </Text>
                    </View>
                    <View style={styles.recentBadgeCol}>
                      {getUrgencyBadge(item.category)}
                    </View>
                  </View>
                </Card>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background
  },
  scrollContent: {
    padding: Spacing.md,
    paddingTop: 16,
    paddingBottom: 40
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.md
  },
  greeting: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted
  },
  patientName: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  profileBadge: {
    backgroundColor: Colors.blueTint,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    borderRadius: 16
  },
  profileBadgeText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.blueAccent
  },
  startCard: {
    backgroundColor: Colors.surface,
    borderColor: Colors.blueAccent,
    borderWidth: 1.5,
    padding: Spacing.lg,
    marginBottom: Spacing.lg
  },
  startRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between"
  },
  startTextCol: {
    flex: 1,
    marginRight: Spacing.md
  },
  startBadge: {
    fontSize: 10,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.blueAccent,
    letterSpacing: 1,
    marginBottom: 4
  },
  startTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    lineHeight: 22,
    marginBottom: 6
  },
  startDesc: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    lineHeight: 18
  },
  startIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: Colors.blueTint,
    justifyContent: "center",
    alignItems: "center"
  },
  startIcon: {
    fontSize: 24
  },
  startBtn: {
    marginTop: Spacing.md
  },
  sectionTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: Spacing.sm
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.sm
  },
  seeAllText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.blueAccent
  },
  tilesGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: Spacing.lg
  },
  tile: {
    flex: 1,
    minWidth: "22%",
    backgroundColor: Colors.surface,
    borderRadius: Spacing.cardRadius,
    padding: Spacing.md,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: Colors.navyPrimary,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1
  },
  tileIcon: {
    fontSize: 24,
    marginBottom: 4
  },
  tileTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  tileSubtitle: {
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 2
  },
  recentSection: {
    marginBottom: Spacing.lg
  },
  emptyCard: {
    alignItems: "center",
    paddingVertical: Spacing.xl
  },
  emptyIcon: {
    fontSize: 32,
    marginBottom: Spacing.sm
  },
  emptyTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  emptyDesc: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: "center",
    marginTop: 4,
    paddingHorizontal: Spacing.md
  },
  recentCard: {
    padding: Spacing.md,
    marginBottom: Spacing.xs
  },
  recentRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  recentCol: {
    flex: 1
  },
  recentSymptom: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  recentDate: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 2
  },
  recentBadgeCol: {
    marginLeft: Spacing.md
  }
});
