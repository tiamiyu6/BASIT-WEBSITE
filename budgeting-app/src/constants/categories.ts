import { Category } from '../types';

export const DEFAULT_CATEGORIES: Category[] = [
  { id: 'exp-food', name: 'Food', icon: '🍔', color: '#F97316', type: 'expense' },
  { id: 'exp-transport', name: 'Transport', icon: '🚗', color: '#3B82F6', type: 'expense' },
  { id: 'exp-housing', name: 'Housing', icon: '🏠', color: '#8B5CF6', type: 'expense' },
  { id: 'exp-utilities', name: 'Utilities', icon: '💡', color: '#EAB308', type: 'expense' },
  { id: 'exp-entertainment', name: 'Entertainment', icon: '🎬', color: '#EC4899', type: 'expense' },
  { id: 'exp-health', name: 'Health', icon: '💊', color: '#EF4444', type: 'expense' },
  { id: 'exp-shopping', name: 'Shopping', icon: '🛍️', color: '#14B8A6', type: 'expense' },
  { id: 'exp-other', name: 'Other', icon: '📦', color: '#6B7280', type: 'expense' },
  { id: 'inc-salary', name: 'Salary', icon: '💼', color: '#22C55E', type: 'income' },
  { id: 'inc-freelance', name: 'Freelance', icon: '🧑‍💻', color: '#0EA5E9', type: 'income' },
  { id: 'inc-gifts', name: 'Gifts', icon: '🎁', color: '#A855F7', type: 'income' },
  { id: 'inc-other', name: 'Other Income', icon: '💰', color: '#84CC16', type: 'income' },
];

export const CURRENCIES: { code: string; symbol: string; label: string }[] = [
  { code: 'USD', symbol: '$', label: 'US Dollar' },
  { code: 'EUR', symbol: '€', label: 'Euro' },
  { code: 'GBP', symbol: '£', label: 'British Pound' },
  { code: 'NGN', symbol: '₦', label: 'Nigerian Naira' },
  { code: 'CAD', symbol: 'CA$', label: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', label: 'Australian Dollar' },
];
