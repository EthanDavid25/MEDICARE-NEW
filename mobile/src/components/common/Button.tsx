import React from "react";
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from "react-native";
import { Colors } from "../../theme/colors";
import { Typography } from "../../theme/typography";
import { Spacing } from "../../theme/spacing";

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "danger" | "emergency" | "outline";
  size?: "small" | "medium" | "large";
  fullWidth?: boolean;
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
  size = "medium",
  fullWidth = false,
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
      case "emergency":
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
      case "emergency":
        return styles.dangerText;
      case "outline":
        return styles.outlineText;
      default:
        return styles.primaryText;
    }
  };

  const getSizeStyle = () => {
    switch (size) {
      case "small":
        return styles.sizeSmall;
      case "large":
        return styles.sizeLarge;
      default:
        return styles.sizeMedium;
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.baseContainer,
        getSizeStyle(),
        getContainerStyle(),
        fullWidth && styles.fullWidth,
        disabled && styles.disabledContainer,
        style
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === "outline" ? Colors.blueAccent : Colors.textLight}
        />
      ) : (
        <>
          {icon}
          <Text style={[styles.baseText, getTextStyle(), textStyle]}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  baseContainer: {
    borderRadius: Spacing.buttonRadius,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.sm
  },
  sizeSmall: {
    paddingVertical: Spacing.xs,
    paddingHorizontal: Spacing.md,
    minHeight: 36
  },
  sizeMedium: {
    paddingVertical: Spacing.sm + 2,
    paddingHorizontal: Spacing.lg,
    minHeight: 46
  },
  sizeLarge: {
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.xl,
    minHeight: 52
  },
  fullWidth: {
    width: "100%"
  },
  primaryContainer: {
    backgroundColor: Colors.navyPrimary
  },
  secondaryContainer: {
    backgroundColor: Colors.blueAccent
  },
  dangerContainer: {
    backgroundColor: Colors.emergency
  },
  outlineContainer: {
    backgroundColor: "transparent",
    borderWidth: 1.5,
    borderColor: Colors.navyPrimary
  },
  disabledContainer: {
    backgroundColor: Colors.disabled,
    borderColor: Colors.disabled,
    opacity: 0.6
  },
  baseText: {
    fontSize: 14,
    fontWeight: "600"
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
    color: Colors.navyPrimary
  }
});
