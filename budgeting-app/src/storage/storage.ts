import AsyncStorage from '@react-native-async-storage/async-storage';

const PREFIX = '@budgeting_app';

export const STORAGE_KEYS = {
  categories: `${PREFIX}/categories`,
  transactions: `${PREFIX}/transactions`,
  budgets: `${PREFIX}/budgets`,
  recurring: `${PREFIX}/recurring`,
  settings: `${PREFIX}/settings`,
} as const;

export async function loadJSON<T>(key: string, fallback: T): Promise<T> {
  const raw = await AsyncStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export async function saveJSON<T>(key: string, value: T): Promise<void> {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

export async function clearAll(): Promise<void> {
  await AsyncStorage.removeMany(Object.values(STORAGE_KEYS));
}
