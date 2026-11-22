import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  ScrollView,
  TouchableOpacity,
  Alert
} from "react-native";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { Spacing } from "../theme/spacing";
import { Button } from "../components/common/Button";
import { Card } from "../components/common/Card";
import { validateIndianMobile } from "../clinical/offlineEngine";
import { AsyncStorageWrapper } from "../storage/asyncStorage";
import { PatientProfile } from "../types";

interface RegistrationScreenProps {
  navigation: any;
}

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"];
const CHRONIC_CONDITIONS = [
  "Diabetes",
  "Hypertension",
  "Heart Disease",
  "Asthma/COPD",
  "Kidney Disease",
  "None"
];

export const RegistrationScreen: React.FC<RegistrationScreenProps> = ({ navigation }) => {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState<"male" | "female" | "other">("male");
  const [phone, setPhone] = useState("");
  const [emergencyPhone, setEmergencyPhone] = useState("");
  const [bloodGroup, setBloodGroup] = useState("Unknown");
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const toggleCondition = (cond: string) => {
    if (cond === "None") {
      setSelectedConditions(["None"]);
      return;
    }
    const filtered = selectedConditions.filter((c) => c !== "None");
    if (filtered.includes(cond)) {
      setSelectedConditions(filtered.filter((c) => c !== cond));
    } else {
      setSelectedConditions([...filtered, cond]);
    }
  };

  const handleRegister = async () => {
    // 1. Validate Name
    if (!name.trim()) {
      Alert.alert("Required Field", "Please enter your full name.");
      return;
    }

    // 2. Validate Age
    const parsedAge = parseInt(age, 10);
    if (isNaN(parsedAge) || parsedAge < 1 || parsedAge > 120) {
      Alert.alert("Invalid Age", "Please enter a valid age between 1 and 120.");
      return;
    }

    // 3. Validate Indian Mobile
    const mobileValidation = validateIndianMobile(phone);
    if (!mobileValidation.isValid) {
      setPhoneError(mobileValidation.errorMessage || "Invalid 10-digit Indian mobile number.");
      Alert.alert("Invalid Mobile Number", mobileValidation.errorMessage || "Please enter a valid 10-digit Indian phone number starting with 6, 7, 8, or 9.");
      return;
    }
    setPhoneError(null);

    // 4. Validate Emergency Phone if provided
    let formattedEmergency = "";
    if (emergencyPhone.trim()) {
      const emValidation = validateIndianMobile(emergencyPhone);
      if (!emValidation.isValid) {
        Alert.alert("Invalid Emergency Contact", emValidation.errorMessage || "Please enter a valid 10-digit Indian emergency contact number.");
        return;
      }
      formattedEmergency = emValidation.formattedNumber;
    }

    setIsSubmitting(true);
    try {
      const profile: PatientProfile = {
        name: name.trim(),
        age: parsedAge,
        gender,
        phone: mobileValidation.formattedNumber,
        emergency_contact: formattedEmergency || undefined,
        blood_group: bloodGroup,
        medical_conditions: selectedConditions.filter((c) => c !== "None")
      };

      await AsyncStorageWrapper.savePatientProfile(profile);
      navigation.replace("MainTabs");
    } catch (err: any) {
      Alert.alert("Registration Error", err.message || "Failed to save profile.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
      <View style={styles.header}>
        <Text style={styles.title}>Patient Profile</Text>
        <Text style={styles.subtitle}>
          Your demographic data is stored locally on this device and used for clinical urgency calculation.
        </Text>
      </View>

      <Card style={styles.formCard}>
        {/* Full Name */}
        <Text style={styles.label}>Full Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Ramesh Kulkarni"
          placeholderTextColor={Colors.textMuted}
          value={name}
          onChangeText={setName}
          autoCapitalize="words"
        />

        {/* Age & Sex Row */}
        <View style={styles.row}>
          <View style={styles.colHalf}>
            <Text style={styles.label}>Age (Years) *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. 45"
              placeholderTextColor={Colors.textMuted}
              value={age}
              onChangeText={setAge}
              keyboardType="number-pad"
              maxLength={3}
            />
          </View>

          <View style={styles.colHalf}>
            <Text style={styles.label}>Biological Sex *</Text>
            <View style={styles.genderRow}>
              {(["male", "female", "other"] as const).map((g) => (
                <TouchableOpacity
                  key={g}
                  style={[styles.genderBtn, gender === g && styles.genderBtnActive]}
                  onPress={() => setGender(g)}
                >
                  <Text style={[styles.genderBtnText, gender === g && styles.genderBtnTextActive]}>
                    {g.charAt(0).toUpperCase() + g.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* Mobile Number */}
        <Text style={styles.label}>Indian Mobile Number *</Text>
        <View style={[styles.phoneInputRow, phoneError ? styles.inputError : null]}>
          <View style={styles.countryCodeBadge}>
            <Text style={styles.countryCodeText}>+91</Text>
          </View>
          <TextInput
            style={styles.phoneInput}
            placeholder="10-digit mobile (e.g. 9820012345)"
            placeholderTextColor={Colors.textMuted}
            value={phone}
            onChangeText={(text) => {
              setPhone(text);
              if (phoneError) setPhoneError(null);
            }}
            keyboardType="phone-pad"
            maxLength={14}
          />
        </View>
        {phoneError ? <Text style={styles.errorText}>{phoneError}</Text> : (
          <Text style={styles.hintText}>Must be a valid 10-digit number starting with 6, 7, 8, or 9.</Text>
        )}

        {/* Emergency Contact */}
        <Text style={[styles.label, { marginTop: Spacing.md }]}>Emergency Contact (Optional)</Text>
        <View style={styles.phoneInputRow}>
          <View style={styles.countryCodeBadge}>
            <Text style={styles.countryCodeText}>+91</Text>
          </View>
          <TextInput
            style={styles.phoneInput}
            placeholder="10-digit contact number"
            placeholderTextColor={Colors.textMuted}
            value={emergencyPhone}
            onChangeText={setEmergencyPhone}
            keyboardType="phone-pad"
            maxLength={14}
          />
        </View>

        {/* Blood Group */}
        <Text style={[styles.label, { marginTop: Spacing.md }]}>Blood Group</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScroll}>
          {BLOOD_GROUPS.map((bg) => (
            <TouchableOpacity
              key={bg}
              style={[styles.chip, bloodGroup === bg && styles.chipActive]}
              onPress={() => setBloodGroup(bg)}
            >
              <Text style={[styles.chipText, bloodGroup === bg && styles.chipTextActive]}>
                {bg}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Chronic Conditions */}
        <Text style={[styles.label, { marginTop: Spacing.md }]}>Known Chronic Conditions</Text>
        <View style={styles.conditionsWrap}>
          {CHRONIC_CONDITIONS.map((cond) => {
            const isSelected = selectedConditions.includes(cond);
            return (
              <TouchableOpacity
                key={cond}
                style={[styles.conditionChip, isSelected && styles.conditionChipActive]}
                onPress={() => toggleCondition(cond)}
              >
                <Text
                  style={[
                    styles.conditionChipText,
                    isSelected && styles.conditionChipTextActive
                  ]}
                >
                  {isSelected ? "✓ " : "+ "}
                  {cond}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </Card>

      <Button
        title="Complete Registration"
        onPress={handleRegister}
        loading={isSubmitting}
        size="large"
        style={styles.submitBtn}
      />
    </ScrollView>
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
    paddingBottom: 40
  },
  header: {
    marginBottom: Spacing.md
  },
  title: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  subtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginTop: 4,
    lineHeight: 18
  },
  formCard: {
    padding: Spacing.lg,
    marginBottom: Spacing.lg
  },
  label: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary,
    marginBottom: 6,
    textTransform: "uppercase",
    letterSpacing: 0.5
  },
  input: {
    height: 48,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: Spacing.inputRadius,
    paddingHorizontal: Spacing.md,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    backgroundColor: Colors.surface,
    marginBottom: Spacing.md
  },
  inputError: {
    borderColor: Colors.emergency
  },
  row: {
    flexDirection: "row",
    gap: Spacing.md,
    marginBottom: Spacing.sm
  },
  colHalf: {
    flex: 1
  },
  genderRow: {
    flexDirection: "row",
    height: 48,
    gap: 4
  },
  genderBtn: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: Spacing.inputRadius,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface
  },
  genderBtnActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  genderBtnText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.medium
  },
  genderBtnTextActive: {
    color: Colors.navyPrimary,
    fontWeight: Typography.fontWeight.bold
  },
  phoneInputRow: {
    flexDirection: "row",
    height: 48,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: Spacing.inputRadius,
    backgroundColor: Colors.surface,
    overflow: "hidden"
  },
  countryCodeBadge: {
    backgroundColor: Colors.surfaceAlt,
    paddingHorizontal: Spacing.md,
    justifyContent: "center",
    alignItems: "center",
    borderRightWidth: 1,
    borderRightColor: Colors.border
  },
  countryCodeText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.navyPrimary
  },
  phoneInput: {
    flex: 1,
    paddingHorizontal: Spacing.md,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary
  },
  hintText: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 4
  },
  errorText: {
    fontSize: 11,
    color: Colors.emergency,
    marginTop: 4,
    fontWeight: Typography.fontWeight.medium
  },
  chipScroll: {
    flexDirection: "row",
    marginBottom: Spacing.sm
  },
  chip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
    marginRight: 6
  },
  chipActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  chipText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.medium
  },
  chipTextActive: {
    color: Colors.navyPrimary,
    fontWeight: Typography.fontWeight.bold
  },
  conditionsWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 4
  },
  conditionChip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface
  },
  conditionChipActive: {
    borderColor: Colors.blueAccent,
    backgroundColor: Colors.blueTint
  },
  conditionChipText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.medium
  },
  conditionChipTextActive: {
    color: Colors.navyPrimary,
    fontWeight: Typography.fontWeight.bold
  },
  submitBtn: {
    marginTop: Spacing.sm
  }
});
