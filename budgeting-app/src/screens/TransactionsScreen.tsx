import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { TransactionFormModal } from '../components/TransactionFormModal';
import { useBudget } from '../context/BudgetContext';
import { colors, radius, spacing } from '../constants/theme';
import {
  currentMonthKey,
  formatCurrency,
  formatDateLabel,
  formatMonthLabel,
  monthKey,
  shiftMonthKey,
} from '../utils/date';
import { Transaction } from '../types';

interface ListRow {
  key: string;
  isHeader: boolean;
  date?: string;
  transaction?: Transaction;
}

export function TransactionsScreen() {
  const { transactions, getCategoryById, currencySymbol } = useBudget();
  const [month, setMonth] = useState(currentMonthKey());
  const [modalVisible, setModalVisible] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);

  const monthTransactions = useMemo(
    () =>
      transactions
        .filter((t) => monthKey(t.date) === month)
        .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : b.createdAt - a.createdAt)),
    [transactions, month]
  );

  const rows: ListRow[] = useMemo(() => {
    const out: ListRow[] = [];
    let lastDate = '';
    for (const t of monthTransactions) {
      if (t.date !== lastDate) {
        out.push({ key: `h-${t.date}`, isHeader: true, date: t.date });
        lastDate = t.date;
      }
      out.push({ key: t.id, isHeader: false, transaction: t });
    }
    return out;
  }, [monthTransactions]);

  const monthTotal = monthTransactions.reduce(
    (sum, t) => sum + (t.type === 'income' ? t.amount : -t.amount),
    0
  );

  const openAdd = () => {
    setEditing(null);
    setModalVisible(true);
  };

  const openEdit = (t: Transaction) => {
    setEditing(t);
    setModalVisible(true);
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Transactions</Text>
        <Pressable style={styles.addFab} onPress={openAdd}>
          <Text style={styles.addFabText}>+</Text>
        </Pressable>
      </View>

      <View style={styles.monthSelector}>
        <Pressable onPress={() => setMonth((m) => shiftMonthKey(m, -1))} hitSlop={10}>
          <Text style={styles.monthArrow}>‹</Text>
        </Pressable>
        <View style={styles.monthLabelWrap}>
          <Text style={styles.monthLabel}>{formatMonthLabel(month)}</Text>
          <Text style={[styles.monthTotal, { color: monthTotal >= 0 ? colors.income : colors.expense }]}>
            {formatCurrency(monthTotal, currencySymbol)}
          </Text>
        </View>
        <Pressable onPress={() => setMonth((m) => shiftMonthKey(m, 1))} hitSlop={10}>
          <Text style={styles.monthArrow}>›</Text>
        </Pressable>
      </View>

      <FlatList
        data={rows}
        keyExtractor={(r) => r.key}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <Text style={styles.emptyText}>No transactions this month yet.</Text>
        }
        renderItem={({ item }) => {
          if (item.isHeader) {
            return <Text style={styles.dateHeader}>{formatDateLabel(item.date!)}</Text>;
          }
          const t = item.transaction!;
          const category = getCategoryById(t.categoryId);
          return (
            <Pressable style={styles.row} onPress={() => openEdit(t)}>
              <View style={[styles.iconWrap, { backgroundColor: `${category?.color ?? colors.textMuted}22` }]}>
                <Text style={styles.icon}>{category?.icon ?? '💳'}</Text>
              </View>
              <View style={styles.rowInfo}>
                <Text style={styles.rowTitle}>{category?.name ?? 'Uncategorized'}</Text>
                {!!t.note && (
                  <Text style={styles.rowNote} numberOfLines={1}>
                    {t.note}
                  </Text>
                )}
              </View>
              <Text style={[styles.rowAmount, { color: t.type === 'income' ? colors.income : colors.expense }]}>
                {t.type === 'income' ? '+' : '-'}
                {formatCurrency(t.amount, currencySymbol)}
              </Text>
            </Pressable>
          );
        }}
      />

      <TransactionFormModal
        visible={modalVisible}
        editing={editing}
        onClose={() => setModalVisible(false)}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
  },
  addFab: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addFabText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    marginTop: -2,
  },
  monthSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  monthArrow: {
    fontSize: 28,
    color: colors.primary,
    paddingHorizontal: spacing.md,
  },
  monthLabelWrap: {
    alignItems: 'center',
  },
  monthLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  monthTotal: {
    fontSize: 13,
    fontWeight: '600',
    marginTop: 2,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl * 2,
  },
  dateHeader: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.textMuted,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  icon: {
    fontSize: 16,
  },
  rowInfo: {
    flex: 1,
  },
  rowTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  rowNote: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 1,
  },
  rowAmount: {
    fontWeight: '700',
    fontSize: 14,
  },
  emptyText: {
    textAlign: 'center',
    color: colors.textMuted,
    marginTop: spacing.xl,
  },
});
