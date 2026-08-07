# Budget Tracker

A cross-platform (Android + iOS) budgeting app built with [Expo](https://expo.dev) and React Native. All data is stored locally on-device (AsyncStorage) — no account, no backend, fully offline.

This is a standalone project living in its own `budgeting-app/` folder and does not touch or depend on the rest of this repository (the `gbolahon.com` website files).

## Features

- **Income & expense tracking** — add, edit, and delete transactions with amount, category, date, and an optional note.
- **Monthly budgets by category** — set a spending limit per category and see live progress bars, with an over-budget warning.
- **Recurring bills** — track rent, subscriptions, etc. with a frequency (weekly/monthly/yearly), see upcoming/overdue bills, and mark one as paid to auto-log a transaction and roll the due date forward.
- **Insights** — spending breakdown by category and a 6-month income vs. expense trend, plus a savings rate.
- **Settings** — pick a currency, and reset all data if you want a clean slate.

## Tech stack

- Expo SDK 57 (React Native 0.86, React 19) with TypeScript
- React Navigation (bottom tabs)
- `@react-native-async-storage/async-storage` for local persistence
- No other third-party UI/chart libraries — charts and progress bars are lightweight custom components, kept intentionally simple and dependency-free

## Running it

You'll need [Node.js](https://nodejs.org) installed. Then:

```bash
cd budgeting-app
npm install   # first time only
npm start
```

This starts the Expo dev server. From there:

- **On your phone (fastest way to try it):** install the **Expo Go** app from the App Store / Play Store, then scan the QR code shown in the terminal.
- **iOS Simulator** (Mac + Xcode required): press `i` in the terminal, or run `npm run ios`.
- **Android Emulator** (Android Studio required): press `a` in the terminal, or run `npm run android`.

## Building real install files (App Store / Play Store)

For a real .ipa/.apk (or to publish to the stores), use [EAS Build](https://docs.expo.dev/build/introduction/):

```bash
npm install -g eas-cli
eas login
eas build --platform android
eas build --platform ios
```

This requires a free (or paid, for store submission) Expo account, and for iOS you'll need an Apple Developer account to actually publish. `eas build` can produce installable binaries without either of those for testing.

## Project structure

```
budgeting-app/
  App.tsx                     entry point: providers + navigation
  src/
    types/                    shared TypeScript types
    constants/                default categories, currencies, theme
    storage/                  AsyncStorage read/write helpers
    context/BudgetContext.tsx global state + persistence + derived data
    utils/                    date formatting/math helpers
    components/                reusable UI (cards, charts, modals)
    screens/                   one file per tab
    navigation/                bottom tab navigator
```

## Notes / possible next steps

- Reminders for upcoming bills are currently shown in-app (Dashboard "Upcoming Bills" + Recurring screen due badges) rather than as OS push notifications, to keep the app dependency-light and reliable in Expo Go. Real push/local notifications could be added later with `expo-notifications` if wanted.
- Data is local-only by design (per your choice) — if you ever want sync across devices, that would need a backend (e.g. Supabase/Firebase) and a login step.
