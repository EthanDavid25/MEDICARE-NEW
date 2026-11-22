import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";
import { Button } from "../components/common/Button";
import { AsyncStorageWrapper } from "../storage/asyncStorage";
import { AssessmentResult } from "../../shared/types";

interface AssessmentHistoryScreenProps {
  navigation: any;
}

export const AssessmentHistoryScreen: React.FC<AssessmentHistoryScreenProps> = ({ navigation }) => {
  const [history, setHistory] = useState<AssessmentResult[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadHistory = async () => {
    try {
      const past = await AsyncStorageWrapper.getAssessmentHistory();
      setHistory(past);
    } catch (err) {
      console.warn("Failed to load history", err);
    }
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener("focus", () => {
      loadHistory();
    });
    loadHistory();
    return unsubscribe;
  }, [navigation]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  const handleClearHistory = () => {
    Alert.alert(
      "Clear History",
      "Are you sure you want to delete all saved assessment records? This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Clear All",
          style: "destructive",
          onPress: async () => {
            await AsyncStorageWrapper.clearAssessmentHistory();
            setHistory([]);
          }
        }
      ]
    );
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
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Assessment History</Text>
          <Text style={styles.headerSubtitle}>
            {history.length} Saved {history.length === 1 ? "Record" : "Records"} on this device
          </Text>
        </View>
        {history.length > 0 && (
          <TouchableOpacity onPress={handleClearHistory} style={styles.clearBtn}>
            <Text style={styles.clearBtnText}>Clear All</Text>
          </TouchableOpacity>
        )}
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {history.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyIcon}>📂</Text>
            <Text style={styles.emptyTitle}>No Assessment Records</Text>
            <Text style={styles.emptySubtitle}>
              Completed clinical assessments will appear here for your records and doctor consultations.
            </Text>
            <Button
              title="Start New Assessment"
              onPress={() => navigation.navigate("Assessment")}
              style={{ marginTop: Spacing.md }}
            />
          </Card>
        ) : (
          history.map((item, idx) => (
            <TouchableOpacity
              key={item.assessment_id || `hist-full-${idx}`}
              activeOpacity={0.7}
              onPress={() => navigation.navigate("Results", { result: item })}
            >
              <Card style={styles.historyCard}>
                <View style={styles.cardHeader}>
                  <Text style={styles.symptomTitle}>
                    {item.chief_symptom.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </Text>
                  {getUrgencyBadge(item.category)}
                </View>

                <Text style={styles.actionPreview} numberOfLines={2}>
                  {item.recommended_action}
                </Text>

                <View style={styles.metaRow}>
                  <Text style={styles.metaText}>
                    📅 {new Date(item.timestamp).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric"
                    })} • {new Date(item.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </Text>
                  <Text style={styles.scoreText}>Severity: {item.severity_score}/10</Text>
                </View>

                <View style={styles.cardFooter}>
                  <TouchableOpacity
                    style={styles.handoverLink}
                    onPress={() => navigation.navigate("DoctorHandover", { result: item })}
                  >
                    <Text style={styles.handoverLinkText}>📋 Doctor Handover →</Text>
                  </TouchableOpacity>
                </View>
              </Card>
            </TouchableOpacity>
          ))
        )}
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
    borderBottomColor: Colors.border,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
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
  clearBtn: {
    paddingVertical: 4,
    paddingHorizontal: Spacing.sm
  },
  clearBtnText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.emergency
  },
  scrollContent: {
    padding: Spacing.md,
    paddingBottom: 40
  },
  historyCard: {
    padding: Spacing.md,
    marginBottom: Spacing.sm
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: Spacing.xs
  },
  symptomTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    flex: 1,
    marginRight: Spacing.sm
  },
  actionPreview: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    lineHeight: 18,
    marginBottom: Spacing.sm
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: Spacing.xs,
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight
  },
  metaText: {
    fontSize: 11,
    color: Colors.textMuted
  },
  scoreText: {
    fontSize: 11,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  cardFooter: {
    marginTop: Spacing.xs,
    flexDirection: "row",
    justifyContent: "flex-end"
  },
  handoverLink: {
    paddingVertical: 2
  },
  handoverLinkText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.blueAccent
  },
  emptyCard: {
    paddingVertical: 50,
    alignItems: "center"
  },
  emptyIcon: {
    fontSize: 40,
    marginBottom: Spacing.sm
  },
  emptyTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: "center",
    marginTop: 4,
    paddingHorizontal: Spacing.lg
  }
});
