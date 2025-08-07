/**
 * Medical Product Recommender Frontend (Modern TypeScript)
 * Modular, functional approach with composables and services
 */

import type { DOMElements } from '../types/ui';
import { getElementById, toggleClass, toggleVisibility } from './utils/dom';
import { validateSearchQuery } from './utils/validation';
import { useUIState, onStateChange } from './composables/useUIState';
import { usePreferences } from './composables/usePreferences';
import { useApi } from './composables/useApi';
import { processRecommendation, getErrorMessage } from './services/recommendationService';
import { displayResults, displayError, hideAllSections } from './components/resultsDisplay';

/**
 * Initialize DOM elements
 */
function initializeDOMElements(): DOMElements {
  return {
    searchForm: getElementById<HTMLFormElement>('searchForm'),
    searchInput: getElementById<HTMLInputElement>('searchInput'),
    searchButton: getElementById<HTMLButtonElement>('searchButton'),
    searchButtonText: getElementById<HTMLSpanElement>('searchButtonText'),
    loadingSpinner: getElementById<HTMLDivElement>('loadingSpinner'),
    limitSelect: getElementById<HTMLSelectElement>('limitSelect'),
    formatSelect: getElementById<HTMLSelectElement>('formatSelect'),
    resultsSection: getElementById<HTMLElement>('resultsSection'),
    errorSection: getElementById<HTMLElement>('errorSection'),
    noResultsSection: getElementById<HTMLElement>('noResultsSection'),
    queryInfo: getElementById<HTMLDivElement>('queryInfo'),
    queryDetails: getElementById<HTMLDivElement>('queryDetails'),
    productsGrid: getElementById<HTMLDivElement>('productsGrid'),
    errorMessage: getElementById<HTMLParagraphElement>('errorMessage'),
    retryButton: getElementById<HTMLButtonElement>('retryButton'),
    toggleAdvanced: getElementById<HTMLButtonElement>('toggleAdvanced'),
    advancedOptions: getElementById<HTMLDivElement>('advancedOptions'),
    advancedIcon: getElementById<HTMLElement>('advancedIcon'),
  };
}

/**
 * Setup form validation
 */
function setupFormValidation(elements: DOMElements): void {
  elements.searchInput.addEventListener('input', () => {
    const query = elements.searchInput.value.trim();
    const validation = validateSearchQuery(query);
    const { state } = useUIState();

    // Update button state
    elements.searchButton.disabled = !validation.isValid || state.isLoading;

    // Update input styling
    toggleClass(elements.searchInput, 'border-red-300', !validation.isValid && query.length > 0);
  });
}

/**
 * Setup search functionality
 */
function setupSearch(elements: DOMElements): void {
  const { baseUrl } = useApi();

  const handleSearch = async (): Promise<void> => {
    const query = elements.searchInput.value.trim();
    const limit = elements.limitSelect.value;
    const format = elements.formatSelect.value;

    if (!query) return;

    hideAllSections();

    try {
      const data = await processRecommendation(query, limit, format);
      displayResults(data);
    } catch (error) {
      const errorMessage = getErrorMessage(error as Error, baseUrl);
      displayError(new Error(errorMessage), baseUrl);
    }
  };

  // Form submission
  elements.searchForm.addEventListener('submit', (e: SubmitEvent) => {
    e.preventDefault();
    void handleSearch();
  });

  // Retry button
  elements.retryButton.addEventListener('click', () => {
    void handleSearch();
  });
}

/**
 * Setup example buttons
 */
function setupExampleButtons(elements: DOMElements): void {
  const exampleButtons = document.querySelectorAll<HTMLButtonElement>('.example-btn');

  exampleButtons.forEach(btn => {
    btn.addEventListener('click', (e: MouseEvent) => {
      const target = e.target as HTMLButtonElement;
      const query = target.getAttribute('data-query');
      if (query) {
        elements.searchInput.value = query;
        elements.searchForm.dispatchEvent(new Event('submit'));
      }
    });
  });
}

/**
 * Setup advanced options toggle
 */
function setupAdvancedOptions(elements: DOMElements): void {
  const { updatePreference } = usePreferences();

  elements.toggleAdvanced.addEventListener('click', () => {
    const isHidden = elements.advancedOptions.classList.contains('hidden');

    if (isHidden) {
      toggleVisibility(elements.advancedOptions, true);
      elements.advancedIcon.style.transform = 'rotate(180deg)';
    } else {
      toggleVisibility(elements.advancedOptions, false);
      elements.advancedIcon.style.transform = 'rotate(0deg)';
    }

    // Save preference
    updatePreference('advancedVisible', !isHidden);
  });
}

/**
 * Setup preferences sync
 */
function setupPreferences(elements: DOMElements): void {
  const { preferences, updatePreference } = usePreferences();

  // Apply initial preferences
  elements.limitSelect.value = preferences.defaultLimit.toString();
  elements.formatSelect.value = preferences.defaultFormat;

  if (preferences.advancedVisible) {
    toggleVisibility(elements.advancedOptions, true);
    elements.advancedIcon.style.transform = 'rotate(180deg)';
  }

  // Save preferences on change
  [elements.limitSelect, elements.formatSelect].forEach(element => {
    element.addEventListener('change', () => {
      const newLimit = parseInt(elements.limitSelect.value, 10);
      const newFormat = elements.formatSelect.value as 'json' | 'simple';

      updatePreference('defaultLimit', newLimit);
      updatePreference('defaultFormat', newFormat);
    });
  });
}

/**
 * Setup UI state synchronization
 */
function setupUIStatSync(elements: DOMElements): void {
  onStateChange(newState => {
    // Loading state
    if (newState.isLoading) {
      elements.searchButton.disabled = true;
      elements.searchButtonText.textContent = 'Szukam...';
      toggleVisibility(elements.loadingSpinner, true);
      elements.searchInput.disabled = true;
    } else {
      elements.searchButton.disabled = false;
      elements.searchButtonText.textContent = 'Szukaj rekomendacji';
      toggleVisibility(elements.loadingSpinner, false);
      elements.searchInput.disabled = false;
    }
  });
}

/**
 * Setup keyboard navigation
 */
function setupKeyboardNavigation(): void {
  document.addEventListener('keydown', (e: KeyboardEvent) => {
    const { state } = useUIState();

    if (e.key === 'Enter' && !state.isLoading) {
      const focused = document.activeElement as HTMLElement;
      if (focused?.classList.contains('example-btn')) {
        focused.click();
      }
    }
  });
}

/**
 * Show welcome message
 */
function showWelcomeMessage(): void {
  const { baseUrl } = useApi();

  // eslint-disable-next-line no-console
  console.log('🏥 Medical Product Recommender loaded (Modern TypeScript)');
  // eslint-disable-next-line no-console
  console.log(`📡 API URL: ${baseUrl}`);
  // eslint-disable-next-line no-console
  console.log('⚡ Functional + Composables architecture');

  // Auto-focus search input
  setTimeout(() => {
    const searchInput = getElementById<HTMLInputElement>('searchInput');
    searchInput.focus();
  }, 500);
}

/**
 * Initialize the application
 */
function initializeApp(): void {
  try {
    // Initialize DOM elements
    const elements = initializeDOMElements();

    // Setup all functionality
    setupFormValidation(elements);
    setupSearch(elements);
    setupExampleButtons(elements);
    setupAdvancedOptions(elements);
    setupPreferences(elements);
    setupUIStatSync(elements);
    setupKeyboardNavigation();

    // Show welcome message
    showWelcomeMessage();

    // eslint-disable-next-line no-console
    console.log('✅ Medical Product Recommender initialized successfully');
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('❌ Failed to initialize Medical Product Recommender:', error);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);

// Export main functions for potential external use
export { initializeApp, initializeDOMElements };
