import React from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { DashboardScreen } from '../screens/DashboardScreen';
import { TransactionsScreen } from '../screens/TransactionsScreen';
import { BudgetsScreen } from '../screens/BudgetsScreen';
import { RecurringScreen } from '../screens/RecurringScreen';
import { InsightsScreen } from '../screens/InsightsScreen';
import { SettingsScreen } from '../screens/SettingsScreen';
import { colors } from '../constants/theme';

export type RootTabParamList = {
  Dashboard: undefined;
  Transactions: undefined;
  Budgets: undefined;
  Recurring: undefined;
  Insights: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<RootTabParamList>();

const TAB_ICONS: Record<keyof RootTabParamList, string> = {
  Dashboard: '🏠',
  Transactions: '💸',
  Budgets: '🎯',
  Recurring: '🔁',
  Insights: '📊',
  Settings: '⚙️',
};

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.textMuted,
          tabBarIcon: () => <Text style={{ fontSize: 18 }}>{TAB_ICONS[route.name as keyof RootTabParamList]}</Text>,
          tabBarLabelStyle: { fontSize: 11 },
        })}
      >
        <Tab.Screen name="Dashboard" component={DashboardScreen} />
        <Tab.Screen name="Transactions" component={TransactionsScreen} />
        <Tab.Screen name="Budgets" component={BudgetsScreen} />
        <Tab.Screen name="Recurring" component={RecurringScreen} />
        <Tab.Screen name="Insights" component={InsightsScreen} />
        <Tab.Screen name="Settings" component={SettingsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
