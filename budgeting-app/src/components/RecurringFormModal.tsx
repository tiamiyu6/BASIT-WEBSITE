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
import { RecurringFrequency, RecurringItem } from '../types';

interface Props {
  visible: boolean;
  onClose: () => void;
  editing?: RecurringItem | null;
}

const FREQUENCIES: RecurringFrequency[] = ['weekly', 'monthly', 'yearly'];

export function RecurringFormModal({ visible, onClose, editing }: Props) {
  const { categories, addRecurring, updateRecurring, deleteRecurring } = useBudget();
  const expenseCategories = categories.filter((c) => c.type === 'expense');

  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [frequency, setFrequency] = useState<RecurringFrequency>('monthly');
  const [nextDueDate, setNextDueDate] = useState(todayISO());

  useEffect(() => {
    if (!visible) return;
    if (editing) {
      setName(editing.name);
      setAmount(String(editing.amount));
      setCategoryId(editing.categoryId);
      setFrequency(editing.frequency);
      setNextDueDate(editing.nextDueDate);
    } else {
      setName('');
      setAmount('');
      setCategoryId(expenseCategories[0]?.id ?? '');
      setFrequency('monthly');
      setNextDueDate(todayISO());
    }
  }, [visible, editing]);

  const canSave = name.trim().length > 0 && Number(amount) > 0 && !!categoryId && !!nextDueDate;

  const handleSave = () => {
    if (!canSave) return;
    const payload = {
      name: name.trim(),
      amount: Number(amount),
      categoryId,
      frequency,
      nextDueDate,
    };
    if (editing) {
      updateRecurring(editing.id, payload);
    } else {
      addRecurring(payload);
    }
    onClose();
  };

  const handleDelete = () => {
    if (editing) deleteRecurring(editing.id);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <ScrollView keyboardShouldPersistTaps="handled">
            <Text style={styles.title}>{editing ? 'Edit Recurring Bill' : 'Add Recurring Bill'}</Text>

            <Text style={styles.label}>Name</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Rent, Netflix"
              value={name}
              onChangeText={setName}
            />

            <Text style={styles.label}>Amount</Text>
            <TextInput
              style={styles.input}
              keyboardType="decimal-pad"
              placeholder="0.00"
              value={amount}
              onChangeText={(v) => setAmount(v.replace(/[^0-9.]/g, ''))}
            />

            <Text style={styles.label}>Category</Text>
            <View style={styles.categoryGrid}>
              {expenseCategories.map((c) => (
                <Pressable
                  key={c.id}
                  onPress={() => setCategoryId(c.id)}
                  style={[
                    styles.categoryChip,
                    categoryId === c.id && {
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

            <Text style={styles.label}>Frequency</Text>
            <View style={styles.typeToggle}>
              {FREQUENCIES.map((f) => (
                <Pressable
                  key={f}
                  onPress={() => setFrequency(f)}
                  style={[styles.typeButton, frequency === f && { backgroundColor: colors.primary }]}
                >
                  <Text
                    style={[styles.typeButtonText, frequency === f && styles.typeButtonTextActive]}
                  >
                    {f[0].toUpperCase() + f.slice(1)}
                  </Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.label}>Next Due Date (YYYY-MM-DD)</Text>
            <TextInput
              style={styles.input}
              placeholder="YYYY-MM-DD"
              value={nextDueDate}
              onChangeText={setNextDueDate}
            />

            <Pressable
              style={[styles.saveButton, !canSave && styles.saveButtonDisabled]}
              onPress={handleSave}
              disabled={!canSave}
            >
              <Text style={styles.saveButtonText}>{editing ? 'Save Changes' : 'Add Recurring Bill'}</Text>
            </Pressable>

            {editing && (
              <Pressable style={styles.deleteButton} onPress={handleDelete}>
                <Text style={styles.deleteButtonText}>Delete</Text>
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
  typeToggle: {
    flexDirection: 'row',
    backgroundColor: colors.background,
    borderRadius: radius.md,
    padding: spacing.xs,
    gap: spacing.xs,
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
    fontSize: 13,
  },
  typeButtonTextActive: {
    color: '#fff',
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
