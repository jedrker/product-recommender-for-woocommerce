/**
 * Validation utility functions
 */

/**
 * Validate search query
 */
export function validateSearchQuery(query: string): { isValid: boolean; error?: string } {
  const trimmed = query.trim();

  if (trimmed.length === 0) {
    return { isValid: false, error: 'Query cannot be empty' };
  }

  if (trimmed.length < 2) {
    return { isValid: false, error: 'Query must be at least 2 characters long' };
  }

  if (trimmed.length > 100) {
    return { isValid: false, error: 'Query cannot be longer than 100 characters' };
  }

  return { isValid: true };
}

/**
 * Validate form limit value
 */
export function validateLimit(value: string): number {
  const num = parseInt(value, 10);
  if (isNaN(num) || num < 1 || num > 50) {
    return 10; // default
  }
  return num;
}

/**
 * Validate format selection
 */
export function validateFormat(value: string): 'json' | 'simple' {
  return value === 'simple' ? 'simple' : 'json';
}
