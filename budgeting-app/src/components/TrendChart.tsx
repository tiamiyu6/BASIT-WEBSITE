import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../constants/theme';
import { formatMonthLabel } from '../utils/date';

export interface TrendPoint {
  month: string; // YYYY-MM
  income: number;
  expense: number;
}

interface Props {
  points: TrendPoint[];
}

export function TrendChart({ points }: Props) {
  const max = Math.max(1, ...points.flatMap((p) => [p.income, p.expense]));

  return (
    <View style={styles.wrap}>
      <View style={styles.chart}>
        {points.map((p) => (
          <View key={p.month} style={styles.col}>
            <View style={styles.bars}>
              <View
                style={[
                  styles.bar,
                  { height: `${(p.income / max) * 100}%`, backgroundColor: colors.income },
                ]}
              />
              <View style={styles.barGap} />
              <View
                style={[
                  styles.bar,
                  { height: `${(p.expense / max) * 100}%`, backgroundColor: colors.expense },
                ]}
              />
            </View>
            <Text style={styles.monthLabel} numberOfLines={1}>
              {formatMonthLabel(p.month).split(' ')[0].slice(0, 3)}
            </Text>
          </View>
        ))}
      </View>
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.dot, { backgroundColor: colors.income }]} />
          <Text style={styles.legendText}>Income</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.dot, { backgroundColor: colors.expense }]} />
          <Text style={styles.legendText}>Expense</Text>
        </View>
      </View>
    </View>
  );
}

const CHART_HEIGHT = 120;

const styles = StyleSheet.create({
  wrap: {
    width: '100%',
  },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: CHART_HEIGHT,
    justifyContent: 'space-between',
  },
  col: {
    flex: 1,
    alignItems: 'center',
  },
  bars: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: CHART_HEIGHT - 20,
  },
  bar: {
    width: 8,
    minHeight: 2,
    borderRadius: 4,
  },
  barGap: {
    width: 3,
  },
  monthLabel: {
    marginTop: spacing.xs,
    fontSize: 11,
    color: colors.textMuted,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing.md,
    gap: spacing.lg,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendText: {
    fontSize: 12,
    color: colors.textMuted,
  },
});
