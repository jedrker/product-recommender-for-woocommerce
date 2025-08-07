/**
 * User preferences management composable
 */

import type { UserPreferences } from '../../types/ui';

const STORAGE_KEY = 'medical-recommender-preferences';

// Default preferences
const defaultPreferences: UserPreferences = {
  theme: 'auto',
  defaultLimit: 10,
  defaultFormat: 'json',
  advancedVisible: false,
  animationsEnabled: true,
};

// Current preferences
let currentPreferences: UserPreferences = { ...defaultPreferences };

/**
 * Load preferences from localStorage
 */
export function loadPreferences(): UserPreferences {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as Partial<UserPreferences>;
      currentPreferences = {
        ...defaultPreferences,
        ...parsed,
      };
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Failed to load user preferences:', error);
  }

  return { ...currentPreferences };
}

/**
 * Save preferences to localStorage
 */
export function savePreferences(preferences: Partial<UserPreferences>): void {
  try {
    currentPreferences = { ...currentPreferences, ...preferences };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentPreferences));
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Failed to save user preferences:', error);
  }
}

/**
 * Get current preferences
 */
export function getPreferences(): UserPreferences {
  return { ...currentPreferences };
}

/**
 * Update specific preference
 */
export function updatePreference<K extends keyof UserPreferences>(key: K, value: UserPreferences[K]): void {
  savePreferences({ [key]: value });
}

/**
 * Reset preferences to defaults
 */
export function resetPreferences(): void {
  currentPreferences = { ...defaultPreferences };
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Failed to reset preferences:', error);
  }
}

/**
 * Preferences composable
 */
export function usePreferences() {
  // Load preferences on first use
  const preferences = loadPreferences();

  return {
    preferences,
    loadPreferences,
    savePreferences,
    getPreferences,
    updatePreference,
    resetPreferences,
  };
}
