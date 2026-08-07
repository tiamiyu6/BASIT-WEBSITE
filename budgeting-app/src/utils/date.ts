import { RecurringFrequency } from '../types';

function pad(n: number): string {
  return n.toString().padStart(2, '0');
}

export function toISODate(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function todayISO(): string {
  return toISODate(new Date());
}

export function monthKey(isoDate: string): string {
  return isoDate.slice(0, 7); // YYYY-MM
}

export function currentMonthKey(): string {
  return monthKey(todayISO());
}

export function formatMonthLabel(key: string): string {
  const [year, month] = key.split('-').map(Number);
  const date = new Date(year, month - 1, 1);
  return date.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
}

export function formatDateLabel(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

export function daysUntil(isoDate: string): number {
  const [year, month, day] = isoDate.split('-').map(Number);
  const target = new Date(year, month - 1, day);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

export function addInterval(isoDate: string, frequency: RecurringFrequency): string {
  const [year, month, day] = isoDate.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  if (frequency === 'weekly') {
    date.setDate(date.getDate() + 7);
  } else if (frequency === 'monthly') {
    date.setMonth(date.getMonth() + 1);
  } else {
    date.setFullYear(date.getFullYear() + 1);
  }
  return toISODate(date);
}

export function shiftMonthKey(key: string, delta: number): string {
  const [year, month] = key.split('-').map(Number);
  const date = new Date(year, month - 1 + delta, 1);
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}`;
}

export function formatCurrency(amount: number, currencySymbol: string): string {
  const rounded = Math.round(amount * 100) / 100;
  const sign = rounded < 0 ? '-' : '';
  return `${sign}${currencySymbol}${Math.abs(rounded).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}
