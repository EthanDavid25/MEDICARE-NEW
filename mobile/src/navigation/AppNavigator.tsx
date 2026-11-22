import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { SplashScreen } from "../screens/SplashScreen";
import { OnboardingScreen } from "../screens/OnboardingScreen";
import { RegistrationScreen } from "../screens/RegistrationScreen";
import { BottomTabNavigator } from "./BottomTabNavigator";
import { SymptomAssessmentScreen } from "../screens/SymptomAssessmentScreen";
import { AssessmentResultsScreen } from "../screens/AssessmentResultsScreen";
import { DoctorHandoverScreen } from "../screens/DoctorHandoverScreen";
import { HospitalFinderScreen } from "../screens/HospitalFinderScreen";
import { AssessmentHistoryScreen } from "../screens/AssessmentHistoryScreen";
import { SettingsScreen } from "../screens/SettingsScreen";
import { AssessmentResult } from "../types";

export type RootStackParamList = {
  Splash: undefined;
  Onboarding: undefined;
  Registration: undefined;
  MainTabs: undefined;
  Assessment: undefined;
  Results: { result: AssessmentResult };
  DoctorHandover: { result?: AssessmentResult };
  Hospitals: undefined;
  History: undefined;
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export const AppNavigator = () => {
  return (
    <Stack.Navigator
      initialRouteName="Splash"
      screenOptions={{
        headerShown: false,
        animation: "slide_from_right"
      }}
    >
      <Stack.Screen name="Splash" component={SplashScreen} />
      <Stack.Screen name="Onboarding" component={OnboardingScreen} />
      <Stack.Screen name="Registration" component={RegistrationScreen} />
      <Stack.Screen name="MainTabs" component={BottomTabNavigator} />
      <Stack.Screen name="Assessment" component={SymptomAssessmentScreen} />
      <Stack.Screen name="Results" component={AssessmentResultsScreen as any} />
      <Stack.Screen name="DoctorHandover" component={DoctorHandoverScreen as any} />
      <Stack.Screen name="Hospitals" component={HospitalFinderScreen} />
      <Stack.Screen name="History" component={AssessmentHistoryScreen} />
      <Stack.Screen name="Settings" component={SettingsScreen} />
    </Stack.Navigator>
  );
};
