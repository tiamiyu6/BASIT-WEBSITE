import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { DEFAULT_CATEGORIES, CURRENCIES } from '../constants/categories';
import { loadJSON, saveJSON, STORAGE_KEYS, clearAll } from '../storage/storage';
import { generateId } from '../utils/id';
import { addInterval, currentMonthKey, monthKey, todayISO } from '../utils/date';
import {
  AppSettings,
  Budget,
  Category,
  RecurringItem,
  Transaction,
} from '../types';

const DEFAULT_SETTINGS: AppSettings = { currency: 'USD' };

interface BudgetContextValue {
  loading: boolean;
  categories: Category[];
  transactions: Transaction[];
  budgets: Budget[];
  recurring: RecurringItem[];
  settings: AppSettings;
  currencySymbol: string;

  addTransaction: (tx: Omit<Transaction, 'id' | 'createdAt'>) => void;
  updateTransaction: (id: string, patch: Partial<Omit<Transaction, 'id'>>) => void;
  deleteTransaction: (id: string) => void;

  setBudget: (categoryId: string, monthlyLimit: number) => void;
  removeBudget: (categoryId: string) => void;

  addRecurring: (item: Omit<RecurringItem, 'id'>) => void;
  updateRecurring: (id: string, patch: Partial<Omit<RecurringItem, 'id'>>) => void;
  deleteRecurring: (id: string) => void;
  markRecurringPaid: (id: string) => void;

  updateSettings: (patch: Partial<AppSettings>) => void;
  resetAllData: () => Promise<void>;

  getCategoryById: (id: string) => Category | undefined;
  monthTotals: (month: string) => { income: number; expense: number; balance: number };
  categorySpend: (categoryId: string, month: string) => number;
  balance: number;
}

const BudgetContext = createContext<BudgetContextValue | undefined>(undefined);

export function BudgetProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState<Category[]>(DEFAULT_CATEGORIES);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [recurring, setRecurring] = useState<RecurringItem[]>([]);
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);

  useEffect(() => {
    (async () => {
      const [cats, txs, bgs, rec, set] = await Promise.all([
        loadJSON(STORAGE_KEYS.categories, DEFAULT_CATEGORIES),
        loadJSON<Transaction[]>(STORAGE_KEYS.transactions, []),
        loadJSON<Budget[]>(STORAGE_KEYS.budgets, []),
        loadJSON<RecurringItem[]>(STORAGE_KEYS.recurring, []),
        loadJSON<AppSettings>(STORAGE_KEYS.settings, DEFAULT_SETTINGS),
      ]);
      setCategories(cats);
      setTransactions(txs);
      setBudgets(bgs);
      setRecurring(rec);
      setSettings(set);
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (!loading) saveJSON(STORAGE_KEYS.categories, categories);
  }, [categories, loading]);
  useEffect(() => {
    if (!loading) saveJSON(STORAGE_KEYS.transactions, transactions);
  }, [transactions, loading]);
  useEffect(() => {
    if (!loading) saveJSON(STORAGE_KEYS.budgets, budgets);
  }, [budgets, loading]);
  useEffect(() => {
    if (!loading) saveJSON(STORAGE_KEYS.recurring, recurring);
  }, [recurring, loading]);
  useEffect(() => {
    if (!loading) saveJSON(STORAGE_KEYS.settings, settings);
  }, [settings, loading]);

  const addTransaction = useCallback((tx: Omit<Transaction, 'id' | 'createdAt'>) => {
    setTransactions((prev) => [
      { ...tx, id: generateId(), createdAt: Date.now() },
      ...prev,
    ]);
  }, []);

  const updateTransaction = useCallback(
    (id: string, patch: Partial<Omit<Transaction, 'id'>>) => {
      setTransactions((prev) =>
        prev.map((t) => (t.id === id ? { ...t, ...patch } : t))
      );
    },
    []
  );

  const deleteTransaction = useCallback((id: string) => {
    setTransactions((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const setBudget = useCallback((categoryId: string, monthlyLimit: number) => {
    setBudgets((prev) => {
      const existing = prev.find((b) => b.categoryId === categoryId);
      if (existing) {
        return prev.map((b) =>
          b.categoryId === categoryId ? { ...b, monthlyLimit } : b
        );
      }
      return [...prev, { id: generateId(), categoryId, monthlyLimit }];
    });
  }, []);

  const removeBudget = useCallback((categoryId: string) => {
    setBudgets((prev) => prev.filter((b) => b.categoryId !== categoryId));
  }, []);

  const addRecurring = useCallback((item: Omit<RecurringItem, 'id'>) => {
    setRecurring((prev) => [...prev, { ...item, id: generateId() }]);
  }, []);

  const updateRecurring = useCallback(
    (id: string, patch: Partial<Omit<RecurringItem, 'id'>>) => {
      setRecurring((prev) =>
        prev.map((r) => (r.id === id ? { ...r, ...patch } : r))
      );
    },
    []
  );

  const deleteRecurring = useCallback((id: string) => {
    setRecurring((prev) => prev.filter((r) => r.id !== id));
  }, []);

  const markRecurringPaid = useCallback(
    (id: string) => {
      const item = recurring.find((r) => r.id === id);
      if (!item) return;
      const paidDate = todayISO();
      addTransaction({
        type: 'expense',
        amount: item.amount,
        categoryId: item.categoryId,
        date: paidDate,
        note: item.name,
      });
      updateRecurring(id, {
        lastPaidDate: paidDate,
        nextDueDate: addInterval(item.nextDueDate, item.frequency),
      });
    },
    [recurring, addTransaction, updateRecurring]
  );

  const updateSettings = useCallback((patch: Partial<AppSettings>) => {
    setSettings((prev) => ({ ...prev, ...patch }));
  }, []);

  const resetAllData = useCallback(async () => {
    await clearAll();
    setCategories(DEFAULT_CATEGORIES);
    setTransactions([]);
    setBudgets([]);
    setRecurring([]);
    setSettings(DEFAULT_SETTINGS);
  }, []);

  const getCategoryById = useCallback(
    (id: string) => categories.find((c) => c.id === id),
    [categories]
  );

  const monthTotals = useCallback(
    (month: string) => {
      let income = 0;
      let expense = 0;
      for (const t of transactions) {
        if (monthKey(t.date) !== month) continue;
        if (t.type === 'income') income += t.amount;
        else expense += t.amount;
      }
      return { income, expense, balance: income - expense };
    },
    [transactions]
  );

  const categorySpend = useCallback(
    (categoryId: string, month: string) => {
      return transactions
        .filter(
          (t) =>
            t.categoryId === categoryId &&
            t.type === 'expense' &&
            monthKey(t.date) === month
        )
        .reduce((sum, t) => sum + t.amount, 0);
    },
    [transactions]
  );

  const balance = useMemo(() => {
    return transactions.reduce(
      (sum, t) => sum + (t.type === 'income' ? t.amount : -t.amount),
      0
    );
  }, [transactions]);

  const currencySymbol = useMemo(() => {
    return CURRENCIES.find((c) => c.code === settings.currency)?.symbol ?? '$';
  }, [settings.currency]);

  const value: BudgetContextValue = {
    loading,
    categories,
    transactions,
    budgets,
    recurring,
    settings,
    currencySymbol,
    addTransaction,
    updateTransaction,
    deleteTransaction,
    setBudget,
    removeBudget,
    addRecurring,
    updateRecurring,
    deleteRecurring,
    markRecurringPaid,
    updateSettings,
    resetAllData,
    getCategoryById,
    monthTotals,
    categorySpend,
    balance,
  };

  return (
    <BudgetContext.Provider value={value}>{children}</BudgetContext.Provider>
  );
}

export function useBudget(): BudgetContextValue {
  const ctx = useContext(BudgetContext);
  if (!ctx) throw new Error('useBudget must be used within a BudgetProvider');
  return ctx;
}

export { currentMonthKey };
