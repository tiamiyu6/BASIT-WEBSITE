import React, { useEffect, useState } from 'react';
import {
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useBudget } from '../context/BudgetContext';
import { colors, radius, spacing } from '../constants/theme';
import { todayISO } from '../utils/date';
import { Transaction, TransactionType } from '../types';

export interface TransactionDraft {
  type: TransactionType;
  amount: string;
  categoryId: string;
  date: string;
  note: string;
}

interface Props {
  visible: boolean;
  onClose: () => void;
  editing?: Transaction | null;
}

export function TransactionFormModal({ visible, onClose, editing }: Props) {
  const { categories, addTransaction, updateTransaction, deleteTransaction } = useBudget();

  const [draft, setDraft] = useState<TransactionDraft>({
    type: 'expense',
    amount: '',
    categoryId: '',
    date: todayISO(),
    note: '',
  });

  useEffect(() => {
    if (!visible) return;
    if (editing) {
      setDraft({
        type: editing.type,
        amount: String(editing.amount),
        categoryId: editing.categoryId,
        date: editing.date,
        note: editing.note ?? '',
      });
    } else {
      const firstExpense = categories.find((c) => c.type === 'expense');
      setDraft({
        type: 'expense',
        amount: '',
        categoryId: firstExpense?.id ?? '',
        date: todayISO(),
        note: '',
      });
    }
  }, [visible, editing, categories]);

  const availableCategories = categories.filter((c) => c.type === draft.type);

  const handleTypeChange = (type: TransactionType) => {
    const firstOfType = categories.find((c) => c.type === type);
    setDraft((d) => ({ ...d, type, categoryId: firstOfType?.id ?? '' }));
  };

  const canSave = Number(draft.amount) > 0 && !!draft.categoryId;

  const handleSave = () => {
    if (!canSave) return;
    const payload = {
      type: draft.type,
      amount: Number(draft.amount),
      categoryId: draft.categoryId,
      date: draft.date,
      note: draft.note.trim() || undefined,
    };
    if (editing) {
      updateTransaction(editing.id, payload);
    } else {
      addTransaction(payload);
    }
    onClose();
  };

  const handleDelete = () => {
    if (editing) deleteTransaction(editing.id);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <ScrollView keyboardShouldPersistTaps="handled">
            <Text style={styles.title}>{editing ? 'Edit Transaction' : 'Add Transaction'}</Text>

            <View style={styles.typeToggle}>
              {(['expense', 'income'] as TransactionType[]).map((t) => (
                <Pressable
                  key={t}
                  onPress={() => handleTypeChange(t)}
                  style={[
                    styles.typeButton,
                    draft.type === t && {
                      backgroundColor: t === 'expense' ? colors.expense : colors.income,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.typeButtonText,
                      draft.type === t && styles.typeButtonTextActive,
                    ]}
                  >
                    {t === 'expense' ? 'Expense' : 'Income'}
                  </Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.label}>Amount</Text>
            <TextInput
              style={styles.input}
              keyboardType="decimal-pad"
              placeholder="0.00"
              value={draft.amount}
              onChangeText={(v) => setDraft((d) => ({ ...d, amount: v.replace(/[^0-9.]/g, '') }))}
            />

            <Text style={styles.label}>Category</Text>
            <View style={styles.categoryGrid}>
              {availableCategories.map((c) => (
                <Pressable
                  key={c.id}
                  onPress={() => setDraft((d) => ({ ...d, categoryId: c.id }))}
                  style={[
                    styles.categoryChip,
                    draft.categoryId === c.id && {
                      borderColor: c.color,
                      backgroundColor: `${c.color}22`,
                    },
                  ]}
                >
                  <Text style={styles.categoryChipText}>
                    {c.icon} {c.name}
                  </Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.label}>Date (YYYY-MM-DD)</Text>
            <TextInput
              style={styles.input}
              placeholder="YYYY-MM-DD"
              value={draft.date}
              onChangeText={(v) => setDraft((d) => ({ ...d, date: v }))}
            />

            <Text style={styles.label}>Note (optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="Add a note"
              value={draft.note}
              onChangeText={(v) => setDraft((d) => ({ ...d, note: v }))}
            />

            <Pressable
              style={[styles.saveButton, !canSave && styles.saveButtonDisabled]}
              onPress={handleSave}
              disabled={!canSave}
            >
              <Text style={styles.saveButtonText}>{editing ? 'Save Changes' : 'Add Transaction'}</Text>
            </Pressable>

            {editing && (
              <Pressable style={styles.deleteButton} onPress={handleDelete}>
                <Text style={styles.deleteButtonText}>Delete Transaction</Text>
              </Pressable>
            )}

            <Pressable style={styles.cancelButton} onPress={onClose}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </Pressable>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.lg,
    padding: spacing.lg,
    maxHeight: '88%',
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.lg,
  },
  typeToggle: {
    flexDirection: 'row',
    backgroundColor: colors.background,
    borderRadius: radius.md,
    padding: spacing.xs,
    marginBottom: spacing.lg,
  },
  typeButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    borderRadius: radius.sm,
    alignItems: 'center',
  },
  typeButtonText: {
    color: colors.textMuted,
    fontWeight: '600',
  },
  typeButtonTextActive: {
    color: '#fff',
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textMuted,
    marginBottom: spacing.xs,
    marginTop: spacing.md,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: 16,
    color: colors.text,
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  categoryChip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  categoryChipText: {
    color: colors.text,
    fontSize: 13,
  },
  saveButton: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.xl,
  },
  saveButtonDisabled: {
    opacity: 0.5,
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 15,
  },
  deleteButton: {
    alignItems: 'center',
    paddingVertical: spacing.md,
    marginTop: spacing.sm,
  },
  deleteButtonText: {
    color: colors.danger,
    fontWeight: '600',
  },
  cancelButton: {
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  cancelButtonText: {
    color: colors.textMuted,
  },
});
