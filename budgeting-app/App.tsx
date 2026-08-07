import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { BudgetProvider } from './src/context/BudgetContext';
import { RootNavigator } from './src/navigation/RootNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <BudgetProvider>
        <RootNavigator />
        <StatusBar style="auto" />
      </BudgetProvider>
    </SafeAreaProvider>
  );
}
