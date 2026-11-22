import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Linking, Platform } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";
import { Badge } from "../common/Badge";
import { HospitalFacility } from "../../../shared/types";

interface HospitalCardProps {
  hospital: HospitalFacility;
  onPressDetails?: () => void;
}

export const HospitalCard: React.FC<HospitalCardProps> = ({ hospital, onPressDetails }) => {
  const handleCall = () => {
    if (hospital.phone) {
      Linking.openURL(`tel:${hospital.phone.replace(/[^0-9+]/g, "")}`);
    }
  };

  const handleDirections = () => {
    const scheme = Platform.select({ ios: "maps:0,0?q=", android: "geo:0,0?q=" });
    const latLng = `${hospital.latitude},${hospital.longitude}`;
    const label = encodeURIComponent(hospital.name);
    const url = Platform.select({
      ios: `${scheme}${label}@${latLng}`,
      android: `${scheme}${latLng}(${label})`
    }) || `https://www.google.com/maps/search/?api=1&query=${hospital.latitude},${hospital.longitude}`;

    Linking.openURL(url);
  };

  const formattedDistance = hospital.distance_km !== undefined
    ? `${hospital.distance_km.toFixed(1)} km away`
    : null;

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <View style={styles.titleContainer}>
          <Text style={styles.nameText} numberOfLines={2}>
            {hospital.name}
          </Text>
          <Text style={styles.cityText}>
            {hospital.locality ? `${hospital.locality}, ${hospital.city}` : hospital.city}
          </Text>
        </View>
        {formattedDistance && (
          <View style={styles.distanceBadge}>
            <Text style={styles.distanceText}>{formattedDistance}</Text>
          </View>
        )}
      </View>

      <View style={styles.badgeRow}>
        {hospital.has_emergency && (
          <Badge text="24/7 Emergency" variant="danger" size="small" />
        )}
        {hospital.tier && (
          <Badge text={hospital.tier.toUpperCase()} variant="info" size="small" />
        )}
        {hospital.type && (
          <Badge
            text={hospital.type === "government" ? "Govt Hospital" : "Private Hospital"}
            variant="neutral"
            size="small"
          />
        )}
      </View>

      <Text style={styles.addressText} numberOfLines={2}>
        {hospital.address}
      </Text>

      {hospital.capabilities && hospital.capabilities.length > 0 && (
        <View style={styles.capabilitiesContainer}>
          <Text style={styles.capabilitiesLabel}>Services: </Text>
          <Text style={styles.capabilitiesText} numberOfLines={1}>
            {hospital.capabilities.slice(0, 4).join(" • ")}
          </Text>
        </View>
      )}

      <View style={styles.actionsRow}>
        {hospital.phone ? (
          <TouchableOpacity
            style={styles.actionBtnSecondary}
            onPress={handleCall}
            activeOpacity={0.7}
          >
            <Text style={styles.actionBtnSecondaryText}>📞 Call {hospital.phone}</Text>
          </TouchableOpacity>
        ) : null}

        <TouchableOpacity
          style={styles.actionBtnPrimary}
          onPress={handleDirections}
          activeOpacity={0.7}
        >
          <Text style={styles.actionBtnPrimaryText}>📍 Directions</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: Spacing.cardRadius,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: Colors.navyPrimary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
    marginBottom: Spacing.md
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: Spacing.xs
  },
  titleContainer: {
    flex: 1,
    marginRight: Spacing.sm
  },
  nameText: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    lineHeight: 22
  },
  cityText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 2
  },
  distanceBadge: {
    backgroundColor: Colors.blueTint,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: 12
  },
  distanceText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.blueAccent
  },
  badgeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginVertical: Spacing.xs
  },
  addressText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginVertical: Spacing.xs,
    lineHeight: 16
  },
  capabilitiesContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 4
  },
  capabilitiesLabel: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textMuted
  },
  capabilitiesText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.navyPrimary,
    flex: 1
  },
  actionsRow: {
    flexDirection: "row",
    justifyContent: "flex-end",
    gap: Spacing.sm,
    marginTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.borderLight,
    paddingTop: Spacing.sm
  },
  actionBtnSecondary: {
    flex: 1,
    backgroundColor: Colors.surfaceAlt,
    borderRadius: Spacing.buttonRadius,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: Colors.border
  },
  actionBtnSecondaryText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.navyPrimary
  },
  actionBtnPrimary: {
    flex: 1,
    backgroundColor: Colors.navyPrimary,
    borderRadius: Spacing.buttonRadius,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    alignItems: "center",
    justifyContent: "center"
  },
  actionBtnPrimaryText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.white
  }
});
