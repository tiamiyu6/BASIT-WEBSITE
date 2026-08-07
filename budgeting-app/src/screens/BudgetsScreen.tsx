import React, { useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';
import { useBudget } from '../context/BudgetContext';
import { colors, radius, spacing } from '../constants/theme';
import { currentMonthKey, formatCurrency, formatMonthLabel } from '../utils/date';

export function BudgetsScreen() {
  const { categories, budgets, categorySpend, setBudget, removeBudget, currencySymbol } = useBudget();
  const month = currentMonthKey();
  const expenseCategories = categories.filter((c) => c.type === 'expense');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftValue, setDraftValue] = useState('');

  const startEdit = (categoryId: string, current?: number) => {
    setEditingId(categoryId);
    setDraftValue(current ? String(current) : '');
  };

  const save = (categoryId: string) => {
    const value = Number(draftValue);
    if (value > 0) {
      setBudget(categoryId, value);
    } else {
      removeBudget(categoryId);
    }
    setEditingId(null);
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Budgets</Text>
        <Text style={styles.headerSubtitle}>{formatMonthLabel(month)}</Text>
      </View>

      <FlatList
        data={expenseCategories}
        keyExtractor={(c) => c.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item: category }) => {
          const budget = budgets.find((b) => b.categoryId === category.id);
          const spent = categorySpend(category.id, month);
          const progress = budget ? spent / budget.monthlyLimit : 0;
          const isEditing = editingId === category.id;

          return (
            <Card>
              <View style={styles.rowTop}>
                <Text style={styles.categoryLabel}>
                  {category.icon} {category.name}
                </Text>
                {!isEditing && (
                  <Pressable onPress={() => startEdit(category.id, budget?.monthlyLimit)}>
                    <Text style={styles.editLink}>{budget ? 'Edit' : 'Set limit'}</Text>
                  </Pressable>
                )}
              </View>

              {isEditing ? (
                <View style={styles.editRow}>
                  <TextInput
                    style={styles.input}
                    keyboardType="decimal-pad"
                    placeholder="Monthly limit"
                    value={draftValue}
                    autoFocus
                    onChangeText={(v) => setDraftValue(v.replace(/[^0-9.]/g, ''))}
                  />
                  <Pressable style={styles.saveBtn} onPress={() => save(category.id)}>
                    <Text style={styles.saveBtnText}>Save</Text>
                  </Pressable>
                  <Pressable style={styles.cancelBtn} onPress={() => setEditingId(null)}>
                    <Text style={styles.cancelBtnText}>Cancel</Text>
                  </Pressable>
                </View>
              ) : budget ? (
                <>
                  <View style={styles.spendRow}>
                    <Text style={styles.spendText}>
                      {formatCurrency(spent, currencySymbol)} of {formatCurrency(budget.monthlyLimit, currencySymbol)}
                    </Text>
                    <Text
                      style={[
                        styles.spendPercent,
                        { color: progress > 1 ? colors.danger : colors.textMuted },
                      ]}
                    >
                      {Math.round(progress * 100)}%
                    </Text>
                  </View>
                  <ProgressBar progress={progress} color={category.color} />
                  {progress > 1 && (
                    <Text style={styles.overText}>
                      Over budget by {formatCurrency(spent - budget.monthlyLimit, currencySymbol)}
                    </Text>
                  )}
                </>
              ) : (
                <Text style={styles.noBudgetText}>No budget set for this category.</Text>
              )}
            </Card>
          );
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    marginBottom: spacing.sm,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
  },
  headerSubtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 2,
  },
  listContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xl * 2,
  },
  rowTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  categoryLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.text,
  },
  editLink: {
    color: colors.primary,
    fontWeight: '600',
    fontSize: 13,
  },
  spendRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  spendText: {
    fontSize: 13,
    color: colors.textMuted,
  },
  spendPercent: {
    fontSize: 13,
    fontWeight: '700',
  },
  overText: {
    color: colors.danger,
    fontSize: 12,
    marginTop: spacing.xs,
  },
  noBudgetText: {
    color: colors.textMuted,
    fontSize: 13,
  },
  editRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: 15,
    color: colors.text,
  },
  saveBtn: {
    backgroundColor: colors.primary,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  saveBtnText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 13,
  },
  cancelBtn: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  cancelBtnText: {
    color: colors.textMuted,
    fontSize: 13,
  },
});
