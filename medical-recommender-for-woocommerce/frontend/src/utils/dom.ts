/**
 * DOM utility functions
 */

/**
 * Type-safe element selector
 */
export function getElementById<T extends HTMLElement>(id: string): T {
  const element = document.getElementById(id) as T | null;
  if (!element) {
    throw new Error(`Element with id '${id}' not found`);
  }
  return element;
}

/**
 * Safe HTML escaping to prevent XSS
 */
export function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Smooth scroll to element
 */
export function scrollToElement(element: HTMLElement, delay = 100): void {
  setTimeout(() => {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }, delay);
}

/**
 * Toggle element visibility with animation
 */
export function toggleVisibility(element: HTMLElement, show: boolean): void {
  if (show) {
    element.classList.remove('hidden');
  } else {
    element.classList.add('hidden');
  }
}

/**
 * Add/remove CSS classes
 */
export function toggleClass(element: HTMLElement, className: string, add: boolean): void {
  if (add) {
    element.classList.add(className);
  } else {
    element.classList.remove(className);
  }
}

/**
 * Create element with animation
 */
export function createAnimatedElement<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className: string,
  index = 0
): HTMLElementTagNameMap[K] {
  const element = document.createElement(tag);
  element.className = className;

  // Initial animation state
  element.style.opacity = '0';
  element.style.transform = 'translateY(20px)';

  // Animate in
  setTimeout(() => {
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
  }, index * 100);

  return element;
}
