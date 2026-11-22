import React from "react";
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "danger" | "outline";
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
  style,
  textStyle,
  icon
}) => {
  const getContainerStyle = () => {
    switch (variant) {
      case "secondary":
        return styles.secondaryContainer;
      case "danger":
        return styles.dangerContainer;
      case "outline":
        return styles.outlineContainer;
      default:
        return styles.primaryContainer;
    }
  };

  const getTextStyle = () => {
    switch (variant) {
      case "secondary":
        return styles.secondaryText;
      case "danger":
        return styles.dangerText;
      case "outline":
        return styles.outlineText;
      default:
        return styles.primaryText;
    }
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
      style={[styles.baseContainer, getContainerStyle(), disabled && styles.disabledContainer, style]}
    >
      {loading ? (
        <ActivityIndicator color={variant === "outline" ? Colors.blueAccent : Colors.textLight} size="small" />
      ) : (
        <>
          {icon}
          <Text style={[styles.baseText, getTextStyle(), disabled && styles.disabledText, textStyle]}>
            {title}
          </Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  baseContainer: {
    height: 48,
    borderRadius: Spacing.buttonRadius,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: Spacing.lg
  },
  primaryContainer: {
    backgroundColor: Colors.blueAccent
  },
  secondaryContainer: {
    backgroundColor: Colors.navyPrimary
  },
  dangerContainer: {
    backgroundColor: Colors.urgentEmergency
  },
  outlineContainer: {
    backgroundColor: "transparent",
    borderWidth: 1.5,
    borderColor: Colors.blueAccent
  },
  disabledContainer: {
    backgroundColor: Colors.disabled,
    borderColor: Colors.disabled
  },
  baseText: {
    ...Typography.button
  },
  primaryText: {
    color: Colors.textLight
  },
  secondaryText: {
    color: Colors.textLight
  },
  dangerText: {
    color: Colors.textLight
  },
  outlineText: {
    color: Colors.blueAccent
  },
  disabledText: {
    color: Colors.surfaceSubtle
  }
});
