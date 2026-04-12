/**
 * Navigation structure:
 *
 * Root: Stack
 *   └─ Onboarding (shown while bootstrapping)
 *   └─ Main (shown once user is confirmed)
 *       └─ BottomTabs
 *           ├─ Study tab (inner Stack)
 *           │   ├─ FreeRecall
 *           │   ├─ MCQ          (replace, no back)
 *           │   └─ Explanation  (replace, no back)
 *           ├─ Decks tab (inner Stack)
 *           │   ├─ DeckLibrary
 *           │   ├─ DeckUpload
 *           │   └─ DeckEdit
 *           ├─ Dashboard tab
 *           └─ Settings tab
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text } from 'react-native';

import { useStore } from '../state/store';
import { OnboardingScreen } from '../screens/OnboardingScreen';
import { FreeRecallScreen } from '../screens/FreeRecallScreen';
import { MCQScreen } from '../screens/MCQScreen';
import { ExplanationScreen } from '../screens/ExplanationScreen';
import { DeckLibraryScreen } from '../screens/DeckLibraryScreen';
import { DeckUploadScreen } from '../screens/DeckUploadScreen';
import { DeckEditScreen } from '../screens/DeckEditScreen';
import { DashboardScreen } from '../screens/DashboardScreen';
import { SettingsScreen } from '../screens/SettingsScreen';
import { colors, font } from '../theme';

const Root = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const StudyStack = createNativeStackNavigator();
const DeckStack = createNativeStackNavigator();

function StudyNavigator() {
  return (
    <StudyStack.Navigator screenOptions={{ headerShown: false }}>
      <StudyStack.Screen name="FreeRecall" component={FreeRecallScreen} />
      <StudyStack.Screen name="MCQ" component={MCQScreen} />
      <StudyStack.Screen name="Explanation" component={ExplanationScreen} />
    </StudyStack.Navigator>
  );
}

function DecksNavigator() {
  return (
    <DeckStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.bg },
        headerTintColor: colors.textPrimary,
        headerBackTitle: 'Back',
      }}
    >
      <DeckStack.Screen name="DeckLibrary" component={DeckLibraryScreen} options={{ headerShown: false }} />
      <DeckStack.Screen name="DeckUpload" component={DeckUploadScreen} options={{ title: 'New Deck' }} />
      <DeckStack.Screen name="DeckEdit" component={DeckEditScreen} options={{ title: 'Edit Deck' }} />
    </DeckStack.Navigator>
  );
}

function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  const icons: Record<string, string> = {
    Study: '⚡', Decks: '📚', Dashboard: '📊', Settings: '⚙️',
  };
  return (
    <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.4 }}>{icons[name] ?? '●'}</Text>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarLabelStyle: { fontSize: font.xs, fontWeight: '600' },
        tabBarIcon: ({ focused }) => <TabIcon name={route.name} focused={focused} />,
      })}
    >
      <Tab.Screen name="Study" component={StudyNavigator} />
      <Tab.Screen name="Decks" component={DecksNavigator} />
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

export function AppNavigator() {
  const user = useStore(s => s.user);

  return (
    <NavigationContainer>
      <Root.Navigator screenOptions={{ headerShown: false }}>
        {user == null ? (
          <Root.Screen name="Onboarding" component={OnboardingScreen} />
        ) : (
          <Root.Screen name="Main" component={MainTabs} />
        )}
      </Root.Navigator>
    </NavigationContainer>
  );
}
