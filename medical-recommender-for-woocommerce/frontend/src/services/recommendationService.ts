/**
 * Recommendation service - handles the main recommendation flow
 */

import type { RecommendationRequest, RecommendationResponse, SimpleRecommendationResponse } from '../../types/api';
import { useApi } from '../composables/useApi';
import { updateUIState } from '../composables/useUIState';
import { validateSearchQuery, validateLimit, validateFormat } from '../utils/validation';

/**
 * Process recommendation request
 */
export async function processRecommendation(
  query: string,
  limit: string,
  format: string
): Promise<RecommendationResponse | SimpleRecommendationResponse> {
  // Validate inputs
  const queryValidation = validateSearchQuery(query);
  if (!queryValidation.isValid) {
    throw new Error(queryValidation.error || 'Invalid query');
  }

  // Prepare request
  const request: RecommendationRequest = {
    input: query.trim(),
    limit: validateLimit(limit),
    format: validateFormat(format),
  };

  // Update UI state
  updateUIState({
    currentQuery: request.input,
    isLoading: true,
    lastError: null,
  });

  try {
    // Fetch recommendations
    const { fetchRecommendations } = useApi();
    const result = await fetchRecommendations(request);

    // Update UI state on success
    updateUIState({
      isLoading: false,
      resultsVisible: true,
      lastError: null,
    });

    return result;
  } catch (error) {
    // Update UI state on error
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    updateUIState({
      isLoading: false,
      resultsVisible: false,
      lastError: errorMessage,
    });

    throw error;
  }
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: Error, apiBaseUrl: string): string {
  if (error.message.includes('Failed to fetch')) {
    return `Nie można połączyć się z serwerem API (${apiBaseUrl}). Sprawdź czy serwer jest uruchomiony.`;
  }

  if (error.message.includes('timeout')) {
    return 'Przekroczono limit czasu zapytania. Spróbuj ponownie.';
  }

  if (error.message) {
    return error.message;
  }

  return 'Wystąpił nieoczekiwany błąd podczas pobierania rekomendacji.';
}
