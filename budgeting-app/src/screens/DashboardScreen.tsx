import React, { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';
import { TransactionFormModal } from '../components/TransactionFormModal';
import { useBudget } from '../context/BudgetContext';
import { colors, spacing } from '../constants/theme';
import { currentMonthKey, daysUntil, formatCurrency, formatMonthLabel } from '../utils/date';

export function DashboardScreen() {
  const {
    loading,
    budgets,
    recurring,
    getCategoryById,
    monthTotals,
    categorySpend,
    balance,
    currencySymbol,
  } = useBudget();
  const [addVisible, setAddVisible] = useState(false);

  const month = currentMonthKey();
  const totals = monthTotals(month);

  const upcomingBills = useMemo(() => {
    return recurring
      .map((r) => ({ ...r, days: daysUntil(r.nextDueDate) }))
      .filter((r) => r.days <= 7)
      .sort((a, b) => a.days - b.days)
      .slice(0, 5);
  }, [recurring]);

  const topBudgets = useMemo(() => {
    return budgets
      .map((b) => {
        const category = getCategoryById(b.categoryId);
        const spent = categorySpend(b.categoryId, month);
        return { ...b, category, spent, progress: b.monthlyLimit > 0 ? spent / b.monthlyLimit : 0 };
      })
      .filter((b) => b.category)
      .sort((a, b) => b.progress - a.progress)
      .slice(0, 4);
  }, [budgets, categorySpend, getCategoryById, month]);

  if (loading) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.loadingText}>Loading…</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Overview</Text>
          <Text style={styles.headerSubtitle}>{formatMonthLabel(month)}</Text>
        </View>

        <Card style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Total Balance</Text>
          <Text style={styles.balanceValue}>{formatCurrency(balance, currencySymbol)}</Text>
          <View style={styles.balanceRow}>
            <View style={styles.balanceItem}>
              <Text style={[styles.balanceItemValue, { color: colors.income }]}>
                +{formatCurrency(totals.income, currencySymbol)}
              </Text>
              <Text style={styles.balanceItemLabel}>Income (month)</Text>
            </View>
            <View style={styles.balanceItem}>
              <Text style={[styles.balanceItemValue, { color: colors.expense }]}>
                -{formatCurrency(totals.expense, currencySymbol)}
              </Text>
              <Text style={styles.balanceItemLabel}>Expense (month)</Text>
            </View>
          </View>
        </Card>

        <Pressable style={styles.addButton} onPress={() => setAddVisible(true)}>
          <Text style={styles.addButtonText}>+ Add Transaction</Text>
        </Pressable>

        {upcomingBills.length > 0 && (
          <Card>
            <Text style={styles.sectionTitle}>Upcoming Bills</Text>
            {upcomingBills.map((bill) => {
              const category = getCategoryById(bill.categoryId);
              const overdue = bill.days < 0;
              return (
                <View key={bill.id} style={styles.billRow}>
                  <Text style={styles.billIcon}>{category?.icon ?? '💳'}</Text>
                  <View style={styles.billInfo}>
                    <Text style={styles.billName}>{bill.name}</Text>
                    <Text style={[styles.billDue, overdue && { color: colors.danger }]}>
                      {overdue
                        ? `Overdue by ${Math.abs(bill.days)}d`
                        : bill.days === 0
                        ? 'Due today'
                        : `Due in ${bill.days}d`}
                    </Text>
                  </View>
                  <Text style={styles.billAmount}>{formatCurrency(bill.amount, currencySymbol)}</Text>
                </View>
              );
            })}
          </Card>
        )}

        {topBudgets.length > 0 && (
          <Card>
            <Text style={styles.sectionTitle}>Budget Progress</Text>
            {topBudgets.map((b) => (
              <View key={b.id} style={styles.budgetRow}>
                <View style={styles.budgetLabelRow}>
                  <Text style={styles.budgetLabel}>
                    {b.category?.icon} {b.category?.name}
                  </Text>
                  <Text style={styles.budgetAmount}>
                    {formatCurrency(b.spent, currencySymbol)} / {formatCurrency(b.monthlyLimit, currencySymbol)}
                  </Text>
                </View>
                <ProgressBar progress={b.progress} color={b.category?.color} />
              </View>
            ))}
          </Card>
        )}

        {upcomingBills.length === 0 && topBudgets.length === 0 && (
          <Card>
            <Text style={styles.emptyText}>
              Add a transaction, set a budget, or add a recurring bill to see your overview here.
            </Text>
          </Card>
        )}
      </ScrollView>

      <TransactionFormModal visible={addVisible} onClose={() => setAddVisible(false)} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.xl,
    textAlign: 'center',
    color: colors.textMuted,
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
  headerSubtitle: {
    fontSize: 14,
    color: colors.textMuted,
    marginTop: 2,
  },
  balanceCard: {
    backgroundColor: colors.primary,
  },
  balanceLabel: {
    color: '#DBEAFE',
    fontSize: 13,
  },
  balanceValue: {
    color: '#fff',
    fontSize: 32,
    fontWeight: '800',
    marginTop: spacing.xs,
  },
  balanceRow: {
    flexDirection: 'row',
    marginTop: spacing.lg,
    gap: spacing.xl,
  },
  balanceItem: {},
  balanceItemValue: {
    fontSize: 15,
    fontWeight: '700',
  },
  balanceItemLabel: {
    color: '#DBEAFE',
    fontSize: 12,
    marginTop: 2,
  },
  addButton: {
    backgroundColor: colors.card,
    borderRadius: 12,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  addButtonText: {
    color: colors.primary,
    fontWeight: '700',
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  billRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  billIcon: {
    fontSize: 18,
    width: 28,
  },
  billInfo: {
    flex: 1,
  },
  billName: {
    color: colors.text,
    fontWeight: '600',
    fontSize: 14,
  },
  billDue: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: 1,
  },
  billAmount: {
    color: colors.text,
    fontWeight: '600',
  },
  budgetRow: {
    marginBottom: spacing.md,
  },
  budgetLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  budgetLabel: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
  budgetAmount: {
    color: colors.textMuted,
    fontSize: 12,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
});
