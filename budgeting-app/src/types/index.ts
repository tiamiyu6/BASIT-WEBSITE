export type TransactionType = 'income' | 'expense';

export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  type: TransactionType;
}

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  categoryId: string;
  date: string; // ISO yyyy-mm-dd
  note?: string;
  createdAt: number;
}

export interface Budget {
  id: string;
  categoryId: string;
  monthlyLimit: number;
}

export type RecurringFrequency = 'weekly' | 'monthly' | 'yearly';

export interface RecurringItem {
  id: string;
  name: string;
  amount: number;
  categoryId: string;
  frequency: RecurringFrequency;
  nextDueDate: string; // ISO yyyy-mm-dd
  lastPaidDate?: string;
}

export interface AppSettings {
  currency: string;
}

export interface AppData {
  categories: Category[];
  transactions: Transaction[];
  budgets: Budget[];
  recurring: RecurringItem[];
  settings: AppSettings;
}
