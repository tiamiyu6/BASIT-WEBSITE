import React, { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card } from '../components/Card';
import { useBudget } from '../context/BudgetContext';
import { CURRENCIES } from '../constants/categories';
import { colors, radius, spacing } from '../constants/theme';

export function SettingsScreen() {
  const { settings, updateSettings, resetAllData } = useBudget();
  const [confirmingReset, setConfirmingReset] = useState(false);

  const handleReset = () => {
    if (!confirmingReset) {
      setConfirmingReset(true);
      return;
    }
    resetAllData();
    setConfirmingReset(false);
    Alert.alert('Data reset', 'All budgeting data has been cleared.');
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Settings</Text>
        </View>

        <Card>
          <Text style={styles.sectionTitle}>Currency</Text>
          <View style={styles.currencyGrid}>
            {CURRENCIES.map((c) => (
              <Pressable
                key={c.code}
                onPress={() => updateSettings({ currency: c.code })}
                style={[
                  styles.currencyChip,
                  settings.currency === c.code && styles.currencyChipActive,
                ]}
              >
                <Text
                  style={[
                    styles.currencyChipText,
                    settings.currency === c.code && styles.currencyChipTextActive,
                  ]}
                >
                  {c.symbol} {c.code}
                </Text>
              </Pressable>
            ))}
          </View>
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.aboutText}>
            All your budgeting data is stored locally on this device only — nothing is uploaded
            anywhere. Uninstalling the app will erase your data.
          </Text>
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>Danger Zone</Text>
          <Pressable style={styles.resetButton} onPress={handleReset}>
            <Text style={styles.resetButtonText}>
              {confirmingReset ? 'Tap again to confirm reset' : 'Reset All Data'}
            </Text>
          </Pressable>
          {confirmingReset && (
            <Pressable onPress={() => setConfirmingReset(false)}>
              <Text style={styles.cancelText}>Cancel</Text>
            </Pressable>
          )}
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xl * 2,
  },
  header: {
    marginBottom: spacing.lg,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  currencyGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  currencyChip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  currencyChipActive: {
    borderColor: colors.primary,
    backgroundColor: `${colors.primary}15`,
  },
  currencyChipText: {
    color: colors.text,
    fontSize: 13,
  },
  currencyChipTextActive: {
    color: colors.primary,
    fontWeight: '700',
  },
  aboutText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  resetButton: {
    backgroundColor: `${colors.danger}15`,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  resetButtonText: {
    color: colors.danger,
    fontWeight: '700',
  },
  cancelText: {
    textAlign: 'center',
    color: colors.textMuted,
    marginTop: spacing.sm,
  },
});
