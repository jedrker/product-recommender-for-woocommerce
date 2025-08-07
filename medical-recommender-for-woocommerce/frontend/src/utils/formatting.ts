/**
 * Formatting utility functions
 */

/**
 * Format price for display
 */
export function formatPrice(price: number): string {
  return `${price.toFixed(2)} PLN`;
}

/**
 * Get confidence color class
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return 'text-green-600';
  if (confidence >= 60) return 'text-yellow-600';
  if (confidence >= 40) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Format confidence percentage
 */
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}
