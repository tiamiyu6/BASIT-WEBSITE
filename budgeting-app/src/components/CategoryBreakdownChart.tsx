import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, radius, spacing } from '../constants/theme';
import { formatCurrency } from '../utils/date';

export interface BreakdownItem {
  id: string;
  label: string;
  icon: string;
  color: string;
  value: number;
}

interface Props {
  items: BreakdownItem[];
  currencySymbol: string;
  emptyLabel?: string;
}

export function CategoryBreakdownChart({ items, currencySymbol, emptyLabel = 'No data yet' }: Props) {
  const sorted = [...items].filter((i) => i.value > 0).sort((a, b) => b.value - a.value);
  const max = sorted.length ? sorted[0].value : 0;

  if (!sorted.length) {
    return (
      <View style={styles.emptyWrap}>
        <Text style={styles.emptyText}>{emptyLabel}</Text>
      </View>
    );
  }

  return (
    <View>
      {sorted.map((item) => (
        <View key={item.id} style={styles.row}>
          <Text style={styles.icon}>{item.icon}</Text>
          <View style={styles.barCol}>
            <View style={styles.labelRow}>
              <Text style={styles.label}>{item.label}</Text>
              <Text style={styles.value}>{formatCurrency(item.value, currencySymbol)}</Text>
            </View>
            <View style={styles.track}>
              <View
                style={[
                  styles.fill,
                  {
                    width: `${max > 0 ? (item.value / max) * 100 : 0}%`,
                    backgroundColor: item.color,
                  },
                ]}
              />
            </View>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  icon: {
    fontSize: 18,
    width: 28,
  },
  barCol: {
    flex: 1,
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  label: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
  value: {
    color: colors.textMuted,
    fontSize: 13,
  },
  track: {
    height: 8,
    borderRadius: radius.sm,
    backgroundColor: colors.border,
    overflow: 'hidden',
  },
  fill: {
    height: 8,
    borderRadius: radius.sm,
  },
  emptyWrap: {
    paddingVertical: spacing.lg,
    alignItems: 'center',
  },
  emptyText: {
    color: colors.textMuted,
  },
});
