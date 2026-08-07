import React, { useMemo } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card } from '../components/Card';
import { CategoryBreakdownChart } from '../components/CategoryBreakdownChart';
import { TrendChart } from '../components/TrendChart';
import { useBudget } from '../context/BudgetContext';
import { colors, spacing } from '../constants/theme';
import { currentMonthKey, formatCurrency, formatMonthLabel, shiftMonthKey } from '../utils/date';

const TREND_MONTHS = 6;

export function InsightsScreen() {
  const { categories, monthTotals, categorySpend, currencySymbol } = useBudget();
  const month = currentMonthKey();
  const totals = monthTotals(month);

  const breakdown = useMemo(() => {
    return categories
      .filter((c) => c.type === 'expense')
      .map((c) => ({
        id: c.id,
        label: c.name,
        icon: c.icon,
        color: c.color,
        value: categorySpend(c.id, month),
      }));
  }, [categories, categorySpend, month]);

  const trend = useMemo(() => {
    const months: string[] = [];
    let m = month;
    for (let i = 0; i < TREND_MONTHS; i++) {
      months.unshift(m);
      m = shiftMonthKey(m, -1);
    }
    return months.map((mk) => ({ month: mk, ...monthTotals(mk) }));
  }, [month, monthTotals]);

  const savingsRate = totals.income > 0 ? ((totals.income - totals.expense) / totals.income) * 100 : 0;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Insights</Text>
          <Text style={styles.headerSubtitle}>{formatMonthLabel(month)}</Text>
        </View>

        <Card>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{formatCurrency(totals.income, currencySymbol)}</Text>
              <Text style={styles.statLabel}>Income</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{formatCurrency(totals.expense, currencySymbol)}</Text>
              <Text style={styles.statLabel}>Expense</Text>
            </View>
            <View style={styles.statItem}>
              <Text
                style={[styles.statValue, { color: savingsRate >= 0 ? colors.income : colors.expense }]}
              >
                {Math.round(savingsRate)}%
              </Text>
              <Text style={styles.statLabel}>Savings rate</Text>
            </View>
          </View>
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>Last {TREND_MONTHS} Months</Text>
          <TrendChart points={trend} />
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>Spending by Category</Text>
          <CategoryBreakdownChart
            items={breakdown}
            currencySymbol={currencySymbol}
            emptyLabel="No expenses recorded this month yet."
          />
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
  headerSubtitle: {
    fontSize: 14,
    color: colors.textMuted,
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  statLabel: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2,
  },
});
