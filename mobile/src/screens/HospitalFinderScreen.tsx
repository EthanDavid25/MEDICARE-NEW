import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { HospitalCard } from "../components/hospitals/HospitalCard";
import { EmergencyCallBanner } from "../components/hospitals/EmergencyCallBanner";
import { apiClient } from "../api/client";
import { HospitalFacility } from "../../shared/types";

// Default coordinates: Parel, Mumbai (central healthcare hub)
const DEFAULT_LAT = 18.9902;
const DEFAULT_LON = 72.8427;

const FILTER_OPTIONS = ["All", "24/7 Emergency", "Government", "Private", "Tertiary"];

export const HospitalFinderScreen: React.FC = () => {
  const [hospitals, setHospitals] = useState<HospitalFacility[]>([]);
  const [filteredHospitals, setFilteredHospitals] = useState<HospitalFacility[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadHospitals = async () => {
    try {
      setLoading(true);
      const results = await apiClient.getNearbyHospitals(DEFAULT_LAT, DEFAULT_LON, 200);
      setHospitals(results);
      applyFilter(results, activeFilter, searchQuery);
    } catch (err) {
      console.warn("Failed to load hospitals", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHospitals();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHospitals();
    setRefreshing(false);
  };

  const applyFilter = (
    list: HospitalFacility[],
    filter: string,
    query: string
  ) => {
    let result = [...list];

    // Text search
    if (query.trim()) {
      const q = query.toLowerCase();
      result = result.filter(
        (h) =>
          h.name.toLowerCase().includes(q) ||
          h.city.toLowerCase().includes(q) ||
          (h.locality && h.locality.toLowerCase().includes(q)) ||
          h.address.toLowerCase().includes(q)
      );
    }

    // Category filter
    if (filter === "24/7 Emergency") {
      result = result.filter((h) => h.has_emergency);
    } else if (filter === "Government") {
      result = result.filter((h) => h.type.toLowerCase() === "government");
    } else if (filter === "Private") {
      result = result.filter((h) => h.type.toLowerCase() === "private");
    } else if (filter === "Tertiary") {
      result = result.filter((h) => h.tier.toLowerCase() === "tertiary");
    }

    setFilteredHospitals(result);
  };

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter);
    applyFilter(hospitals, filter, searchQuery);
  };

  const handleSearchChange = (text: string) => {
    setSearchQuery(text);
    applyFilter(hospitals, activeFilter, text);
  };

  return (
    <View style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Healthcare Directory</Text>
        <Text style={styles.headerSubtitle}>
          14 Verified Emergency & Tertiary Facilities across Maharashtra
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Emergency Helpline Banner */}
        <EmergencyCallBanner compact />

        {/* Search Bar */}
        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="Search by hospital name, city, or locality..."
            placeholderTextColor={Colors.textMuted}
            value={searchQuery}
            onChangeText={handleSearchChange}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => handleSearchChange("")}>
              <Text style={styles.clearText}>✕</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Filter Chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipsScroll}>
          {FILTER_OPTIONS.map((f) => (
            <TouchableOpacity
              key={f}
              style={[styles.filterChip, activeFilter === f && styles.filterChipActive]}
              onPress={() => handleFilterChange(f)}
            >
              <Text
                style={[styles.filterChipText, activeFilter === f && styles.filterChipTextActive]}
              >
                {f}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Results Count */}
        <View style={styles.countRow}>
          <Text style={styles.countText}>
            Showing {filteredHospitals.length} facilities
          </Text>
          <Text style={styles.regionText}>Maharashtra Region</Text>
        </View>

        {/* Hospital List */}
        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color={Colors.navyPrimary} />
            <Text style={styles.loadingText}>Loading facilities...</Text>
          </View>
        ) : filteredHospitals.length === 0 ? (
          <View style={styles.emptyBox}>
            <Text style={styles.emptyIcon}>🏥</Text>
            <Text style={styles.emptyTitle}>No Facilities Found</Text>
            <Text style={styles.emptySub}>
              Try adjusting your search query or selecting a different filter.
            </Text>
          </View>
        ) : (
          filteredHospitals.map((h) => <HospitalCard key={h.id} hospital={h} />)
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
  searchBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: Spacing.inputRadius,
    paddingHorizontal: Spacing.md,
    height: 48,
    marginBottom: Spacing.sm
  },
  searchIcon: {
    fontSize: 16,
    marginRight: Spacing.sm
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary
  },
  clearText: {
    fontSize: 16,
    color: Colors.textMuted,
    padding: 4
  },
  chipsScroll: {
    flexDirection: "row",
    marginBottom: Spacing.sm
  },
  filterChip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
    marginRight: 6
  },
  filterChipActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueAccent
  },
  filterChipText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.medium
  },
  filterChipTextActive: {
    color: Colors.white,
    fontWeight: Typography.fontWeight.bold
  },
  countRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: Spacing.xs,
    paddingHorizontal: 2
  },
  countText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: Typography.fontWeight.medium
  },
  regionText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.blueAccent,
    fontWeight: Typography.fontWeight.semiBold
  },
  loadingBox: {
    paddingVertical: 50,
    alignItems: "center"
  },
  loadingText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: Spacing.sm
  },
  emptyBox: {
    paddingVertical: 50,
    alignItems: "center"
  },
  emptyIcon: {
    fontSize: 36,
    marginBottom: Spacing.sm
  },
  emptyTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  emptySub: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: "center",
    marginTop: 4,
    paddingHorizontal: Spacing.lg
  }
});
