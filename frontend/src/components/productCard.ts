/**
 * Product Card Component
 */

import type { Product, ProductSummary } from '../../types/api';
import { escapeHtml, createAnimatedElement } from '../utils/dom';
import { formatPrice, truncateText } from '../utils/formatting';

/**
 * Create product card element
 */
export function createProductCard(product: Product | ProductSummary, index: number): HTMLDivElement {
  const card = createAnimatedElement(
    'div',
    'bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow',
    index
  );

  const description = product.description || 'Brak opisu';
  const truncatedDesc = truncateText(description, 120);
  const hasMoreText = description.length > 120;

  card.innerHTML = `
    <div class="flex items-start justify-between mb-3">
      <h3 class="font-semibold text-gray-800 text-sm leading-tight flex-1 pr-2">
        ${escapeHtml(product.name)}
      </h3>
      <span class="text-lg font-bold text-medical-600 whitespace-nowrap">
        ${formatPrice(product.price)}
      </span>
    </div>
    
    <div class="mb-3">
      <span class="inline-block px-2 py-1 bg-medical-100 text-medical-800 text-xs rounded-full">
        <i class="fas fa-tag mr-1"></i>
        ${escapeHtml(product.category)}
      </span>
    </div>
    
    <p class="text-gray-600 text-sm mb-3 leading-relaxed" data-description="${escapeHtml(description)}">
      ${escapeHtml(truncatedDesc)}
    </p>
    
    <div class="flex items-center justify-between text-xs text-gray-500">
      <span>
        <i class="fas fa-hashtag mr-1"></i>
        ID: ${escapeHtml(product.id)}
      </span>
      ${hasMoreText ? createExpandButton() : ''}
    </div>
  `;

  // Add expand functionality if needed
  if (hasMoreText) {
    setupExpandButton(card, description);
  }

  return card;
}

/**
 * Create expand button HTML
 */
function createExpandButton(): string {
  return `
    <button class="expand-btn text-medical-600 hover:text-medical-700 font-medium">
      Więcej <i class="fas fa-chevron-down ml-1"></i>
    </button>
  `;
}

/**
 * Setup expand button functionality
 */
function setupExpandButton(card: HTMLDivElement, fullDescription: string): void {
  const expandBtn = card.querySelector('.expand-btn') as HTMLButtonElement;
  const descriptionEl = card.querySelector('p[data-description]') as HTMLParagraphElement;

  if (expandBtn && descriptionEl) {
    expandBtn.addEventListener('click', () => {
      descriptionEl.textContent = fullDescription;
      expandBtn.style.display = 'none';
    });
  }
}

/**
 * Create multiple product cards
 */
export function createProductCards(products: (Product | ProductSummary)[]): HTMLDivElement[] {
  return products.map((product, index) => createProductCard(product, index));
}
