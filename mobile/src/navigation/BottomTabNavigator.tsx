import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Colors } from "../theme/colors";
import { Typography } from "../theme/typography";
import { DashboardScreen } from "../screens/DashboardScreen";
import { SymptomAssessmentScreen } from "../screens/SymptomAssessmentScreen";
import { HospitalFinderScreen } from "../screens/HospitalFinderScreen";
import { AssessmentHistoryScreen } from "../screens/AssessmentHistoryScreen";
import { SettingsScreen } from "../screens/SettingsScreen";

const Tab = createBottomTabNavigator();

export const BottomTabNavigator = () => {
  return (
    <Tab.Navigator
      initialRouteName="DashboardTab"
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: Colors.navyPrimary,
        tabBarInactiveTintColor: Colors.textMuted,
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabBarLabel,
        tabBarIcon: ({ focused }) => {
          let icon = "🩺";
          if (route.name === "DashboardTab") icon = "🏠";
          else if (route.name === "AssessmentTab") icon = "🩺";
          else if (route.name === "HospitalsTab") icon = "🏥";
          else if (route.name === "HistoryTab") icon = "📑";
          else if (route.name === "SettingsTab") icon = "⚙️";

          return (
            <View style={[styles.iconBox, focused && styles.iconBoxFocused]}>
              <Text style={styles.iconText}>{icon}</Text>
            </View>
          );
        }
      })}
    >
      <Tab.Screen
        name="DashboardTab"
        component={DashboardScreen}
        options={{ tabBarLabel: "Home" }}
      />
      <Tab.Screen
        name="AssessmentTab"
        component={SymptomAssessmentScreen}
        options={{ tabBarLabel: "Assessment" }}
      />
      <Tab.Screen
        name="HospitalsTab"
        component={HospitalFinderScreen}
        options={{ tabBarLabel: "Hospitals" }}
      />
      <Tab.Screen
        name="HistoryTab"
        component={AssessmentHistoryScreen}
        options={{ tabBarLabel: "History" }}
      />
      <Tab.Screen
        name="SettingsTab"
        component={SettingsScreen}
        options={{ tabBarLabel: "Settings" }}
      />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: Colors.surface,
    borderTopColor: Colors.border,
    borderTopWidth: 1,
    height: 64,
    paddingBottom: 8,
    paddingTop: 6,
    elevation: 8,
    shadowColor: Colors.navyPrimary,
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 4
  },
  tabBarLabel: {
    fontSize: 10,
    fontWeight: Typography.fontWeight.medium,
    marginTop: 2
  },
  iconBox: {
    alignItems: "center",
    justifyContent: "center",
    width: 32,
    height: 32,
    borderRadius: 16
  },
  iconBoxFocused: {
    backgroundColor: Colors.blueTint
  },
  iconText: {
    fontSize: 18
  }
});
