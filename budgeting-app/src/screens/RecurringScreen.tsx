import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card } from '../components/Card';
import { RecurringFormModal } from '../components/RecurringFormModal';
import { useBudget } from '../context/BudgetContext';
import { colors, spacing } from '../constants/theme';
import { daysUntil, formatCurrency, formatDateLabel } from '../utils/date';
import { RecurringItem } from '../types';

export function RecurringScreen() {
  const { recurring, getCategoryById, markRecurringPaid, currencySymbol } = useBudget();
  const [modalVisible, setModalVisible] = useState(false);
  const [editing, setEditing] = useState<RecurringItem | null>(null);

  const sorted = useMemo(
    () => [...recurring].sort((a, b) => (a.nextDueDate < b.nextDueDate ? -1 : 1)),
    [recurring]
  );

  const openAdd = () => {
    setEditing(null);
    setModalVisible(true);
  };

  const openEdit = (item: RecurringItem) => {
    setEditing(item);
    setModalVisible(true);
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Recurring Bills</Text>
        <Pressable style={styles.addFab} onPress={openAdd}>
          <Text style={styles.addFabText}>+</Text>
        </Pressable>
      </View>

      <FlatList
        data={sorted}
        keyExtractor={(r) => r.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <Text style={styles.emptyText}>
            No recurring bills yet. Add rent, subscriptions, or other regular payments.
          </Text>
        }
        renderItem={({ item }) => {
          const category = getCategoryById(item.categoryId);
          const days = daysUntil(item.nextDueDate);
          const overdue = days < 0;
          const dueSoon = days >= 0 && days <= 3;
          return (
            <Card>
              <Pressable onPress={() => openEdit(item)}>
                <View style={styles.rowTop}>
                  <Text style={styles.icon}>{category?.icon ?? '💳'}</Text>
                  <View style={styles.info}>
                    <Text style={styles.name}>{item.name}</Text>
                    <Text style={styles.meta}>
                      {category?.name} · {item.frequency}
                    </Text>
                  </View>
                  <Text style={styles.amount}>{formatCurrency(item.amount, currencySymbol)}</Text>
                </View>
                <View style={styles.statusRow}>
                  <Text
                    style={[
                      styles.statusText,
                      overdue && { color: colors.danger },
                      dueSoon && { color: colors.warning },
                    ]}
                  >
                    {overdue
                      ? `Overdue since ${formatDateLabel(item.nextDueDate)}`
                      : days === 0
                      ? 'Due today'
                      : `Due ${formatDateLabel(item.nextDueDate)} (${days}d)`}
                  </Text>
                </View>
              </Pressable>
              <Pressable style={styles.paidBtn} onPress={() => markRecurringPaid(item.id)}>
                <Text style={styles.paidBtnText}>Mark as Paid</Text>
              </Pressable>
            </Card>
          );
        }}
      />

      <RecurringFormModal
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
    marginBottom: spacing.sm,
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
  listContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xl * 2,
  },
  rowTop: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 20,
    width: 32,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.text,
  },
  meta: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 1,
    textTransform: 'capitalize',
  },
  amount: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text,
  },
  statusRow: {
    marginTop: spacing.sm,
  },
  statusText: {
    fontSize: 12,
    color: colors.textMuted,
    fontWeight: '600',
  },
  paidBtn: {
    marginTop: spacing.md,
    backgroundColor: colors.background,
    borderRadius: 10,
    paddingVertical: spacing.sm,
    alignItems: 'center',
  },
  paidBtnText: {
    color: colors.primary,
    fontWeight: '700',
    fontSize: 13,
  },
  emptyText: {
    textAlign: 'center',
    color: colors.textMuted,
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
});
