/**
 * API management composable
 */

import type {
  RecommendationRequest,
  RecommendationResponse,
  SimpleRecommendationResponse,
  ApiErrorResponse,
} from '../../types/api';

/**
 * Get API base URL based on environment
 */
export function getApiBaseUrl(): string {
  const hostname = window.location.hostname;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000';
  } else {
    return `${window.location.protocol}//${hostname}:5000`;
  }
}

/**
 * Fetch recommendations from API
 */
export async function fetchRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse | SimpleRecommendationResponse> {
  const baseUrl = getApiBaseUrl();

  const params = new URLSearchParams({
    input: request.input,
    limit: request.limit?.toString() ?? '10',
    format: request.format ?? 'json',
  });

  const url = `${baseUrl}/recommend?${params}`;

  // eslint-disable-next-line no-console
  console.log(`🔍 Fetching: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    signal: AbortSignal.timeout(30000),
  });

  if (!response.ok) {
    let errorData: ApiErrorResponse;
    try {
      errorData = (await response.json()) as ApiErrorResponse;
    } catch {
      errorData = {
        error: `HTTP ${response.status}: ${response.statusText}`,
        code: 'INTERNAL_ERROR',
      };
    }
    throw new Error(errorData.error);
  }

  const data = (await response.json()) as RecommendationResponse | SimpleRecommendationResponse;
  // eslint-disable-next-line no-console
  console.log('✅ API Response:', data);

  return data;
}

/**
 * API composable
 */
export function useApi() {
  return {
    baseUrl: getApiBaseUrl(),
    fetchRecommendations,
  };
}
