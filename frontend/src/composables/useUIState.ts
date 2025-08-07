/**
 * UI State management composable
 */

import type { UIState } from '../../types/ui';

// Global UI state
let uiState: UIState = {
  isLoading: false,
  currentQuery: '',
  showAdvanced: false,
  lastError: null,
  resultsVisible: false,
};

// State change listeners
type StateListener = (newState: UIState, oldState: UIState) => void;
const listeners: StateListener[] = [];

/**
 * Subscribe to state changes
 */
export function onStateChange(listener: StateListener): () => void {
  listeners.push(listener);

  // Return unsubscribe function
  return () => {
    const index = listeners.indexOf(listener);
    if (index > -1) {
      listeners.splice(index, 1);
    }
  };
}

/**
 * Update UI state
 */
export function updateUIState(updates: Partial<UIState>): void {
  const oldState = { ...uiState };
  uiState = { ...uiState, ...updates };

  // Notify listeners
  listeners.forEach(listener => listener(uiState, oldState));
}

/**
 * Get current UI state
 */
export function getUIState(): UIState {
  return { ...uiState };
}

/**
 * Reset UI state to defaults
 */
export function resetUIState(): void {
  updateUIState({
    isLoading: false,
    currentQuery: '',
    showAdvanced: false,
    lastError: null,
    resultsVisible: false,
  });
}

/**
 * UI state composable
 */
export function useUIState() {
  return {
    state: uiState,
    updateState: updateUIState,
    getState: getUIState,
    resetState: resetUIState,
    onStateChange,
  };
}
