/**
 * Results Display Component
 */

import type { RecommendationResponse, SimpleRecommendationResponse } from '../../types/api';
import { getElementById, escapeHtml, scrollToElement, toggleVisibility } from '../utils/dom';
import { formatConfidence, getConfidenceColor, truncateText } from '../utils/formatting';
import { createProductCards } from './productCard';

/**
 * Display search results
 */
export function displayResults(data: RecommendationResponse | SimpleRecommendationResponse): void {
  if (!data.products || data.products.length === 0) {
    displayNoResults();
    return;
  }

  // Update query info
  updateQueryInfo(data);

  // Display products
  displayProducts(data.products);

  // Show results section
  const resultsSection = getElementById<HTMLElement>('resultsSection');
  toggleVisibility(resultsSection, true);
  scrollToElement(resultsSection);
}

/**
 * Display no results message
 */
export function displayNoResults(): void {
  const noResultsSection = getElementById<HTMLElement>('noResultsSection');
  toggleVisibility(noResultsSection, true);
  scrollToElement(noResultsSection);
}

/**
 * Display error message
 */
export function displayError(error: Error, apiBaseUrl: string): void {
  // eslint-disable-next-line no-console
  console.error('❌ API Error:', error);

  const errorMessage = getElementById<HTMLParagraphElement>('errorMessage');
  const errorSection = getElementById<HTMLElement>('errorSection');

  let errorText = 'Wystąpił nieoczekiwany błąd podczas pobierania rekomendacji.';

  if (error.message.includes('Failed to fetch')) {
    errorText = `Nie można połączyć się z serwerem API (${apiBaseUrl}). Sprawdź czy serwer jest uruchomiony.`;
  } else if (error.message.includes('timeout')) {
    errorText = 'Przekroczono limit czasu zapytania. Spróbuj ponownie.';
  } else if (error.message) {
    errorText = error.message;
  }

  errorMessage.textContent = errorText;
  toggleVisibility(errorSection, true);
  scrollToElement(errorSection);
}

/**
 * Update query information display
 */
function updateQueryInfo(data: RecommendationResponse | SimpleRecommendationResponse): void {
  const queryDetails = getElementById<HTMLDivElement>('queryDetails');
  const confidence = Math.round(data.confidence * 100);
  const confidenceColor = getConfidenceColor(confidence);

  let reasoning = '';
  if ('reasoning' in data && data.reasoning) {
    reasoning = truncateText(data.reasoning, 200);
  }

  queryDetails.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <strong>Zapytanie:</strong><br>
        <span class="font-mono bg-white px-2 py-1 rounded border">${escapeHtml(data.query)}</span>
      </div>
      <div>
        <strong>Pewność:</strong><br>
        <span class="font-semibold ${confidenceColor}">${formatConfidence(data.confidence)}</span>
      </div>
      <div>
        <strong>Znalezionych:</strong><br>
        <span class="font-semibold">${data.count} produktów</span>
      </div>
    </div>
    ${reasoning ? `<div class="mt-3"><strong>Uzasadnienie:</strong><br><span class="text-sm">${escapeHtml(reasoning)}</span></div>` : ''}
  `;
}

/**
 * Display products in grid
 */
function displayProducts(products: (RecommendationResponse | SimpleRecommendationResponse)['products']): void {
  const productsGrid = getElementById<HTMLDivElement>('productsGrid');

  // Clear existing products
  productsGrid.innerHTML = '';

  // Create and append product cards
  const productCards = createProductCards(products);
  productCards.forEach(card => {
    productsGrid.appendChild(card);
  });
}

/**
 * Hide all result sections
 */
export function hideAllSections(): void {
  const sections = [
    getElementById<HTMLElement>('resultsSection'),
    getElementById<HTMLElement>('errorSection'),
    getElementById<HTMLElement>('noResultsSection'),
  ];

  sections.forEach(section => {
    toggleVisibility(section, false);
  });
}
