/**
 * UI and DOM type definitions
 */

// DOM Element selectors
export interface DOMElements {
  readonly searchForm: HTMLFormElement;
  readonly searchInput: HTMLInputElement;
  readonly searchButton: HTMLButtonElement;
  readonly searchButtonText: HTMLSpanElement;
  readonly loadingSpinner: HTMLDivElement;
  readonly limitSelect: HTMLSelectElement;
  readonly formatSelect: HTMLSelectElement;
  readonly resultsSection: HTMLElement;
  readonly errorSection: HTMLElement;
  readonly noResultsSection: HTMLElement;
  readonly queryInfo: HTMLDivElement;
  readonly queryDetails: HTMLDivElement;
  readonly productsGrid: HTMLDivElement;
  readonly errorMessage: HTMLParagraphElement;
  readonly retryButton: HTMLButtonElement;
  readonly toggleAdvanced: HTMLButtonElement;
  readonly advancedOptions: HTMLDivElement;
  readonly advancedIcon: HTMLElement;
}

// UI State
export interface UIState {
  readonly isLoading: boolean;
  readonly currentQuery: string;
  readonly showAdvanced: boolean;
  readonly lastError: string | null;
  readonly resultsVisible: boolean;
}

// Animation types
export type AnimationType = 'fadeIn' | 'slideUp' | 'slideDown' | 'pulse' | 'bounce';

export interface AnimationConfig {
  readonly type: AnimationType;
  readonly duration: number;
  readonly delay?: number;
  readonly easing?: string;
}

// Theme types
export type ThemeMode = 'light' | 'dark' | 'auto';

export interface ThemeConfig {
  readonly mode: ThemeMode;
  readonly colors: ThemeColors;
  readonly fonts: ThemeFonts;
  readonly spacing: ThemeSpacing;
}

export interface ThemeColors {
  readonly primary: string;
  readonly secondary: string;
  readonly success: string;
  readonly warning: string;
  readonly error: string;
  readonly info: string;
  readonly background: string;
  readonly surface: string;
  readonly text: string;
  readonly textSecondary: string;
}

export interface ThemeFonts {
  readonly family: string;
  readonly sizes: {
    readonly xs: string;
    readonly sm: string;
    readonly base: string;
    readonly lg: string;
    readonly xl: string;
    readonly xxl: string;
  };
  readonly weights: {
    readonly normal: number;
    readonly medium: number;
    readonly semibold: number;
    readonly bold: number;
  };
}

export interface ThemeSpacing {
  readonly xs: string;
  readonly sm: string;
  readonly md: string;
  readonly lg: string;
  readonly xl: string;
  readonly xxl: string;
}

// Form types
export interface FormData {
  readonly input: string;
  readonly limit: number;
  readonly format: 'json' | 'simple';
}

export interface FormValidation {
  readonly isValid: boolean;
  readonly errors: FormError[];
}

export interface FormError {
  readonly field: keyof FormData;
  readonly message: string;
  readonly code: string;
}

// Component props
export interface ProductCardProps {
  readonly product: import('./api').Product | import('./api').ProductSummary;
  readonly index: number;
  readonly compact?: boolean;
  readonly onClick?: (product: import('./api').Product) => void;
}

export interface LoadingSpinnerProps {
  readonly size?: 'sm' | 'md' | 'lg';
  readonly color?: string;
  readonly text?: string;
}

export interface ErrorMessageProps {
  readonly message: string;
  readonly type?: 'error' | 'warning' | 'info';
  readonly retryable?: boolean;
  readonly onRetry?: () => void;
}

// Event handlers
export type FormSubmitHandler = (event: SubmitEvent) => void | Promise<void>;
export type InputChangeHandler = (event: Event) => void;
export type ButtonClickHandler = (event: MouseEvent) => void;
export type KeyboardHandler = (event: KeyboardEvent) => void;

// Utility types for DOM manipulation
export interface ElementOptions {
  readonly className?: string;
  readonly id?: string;
  readonly attributes?: Record<string, string>;
  readonly styles?: Partial<CSSStyleDeclaration>;
  readonly dataset?: Record<string, string>;
}

export interface CreateElementOptions<K extends keyof HTMLElementTagNameMap> extends ElementOptions {
  readonly tag: K;
  readonly children?: (HTMLElement | string)[];
  readonly textContent?: string;
  readonly innerHTML?: string;
}

// Responsive breakpoints
export interface Breakpoints {
  readonly xs: number;
  readonly sm: number;
  readonly md: number;
  readonly lg: number;
  readonly xl: number;
}

export type BreakpointName = keyof Breakpoints;

// Media query types
export interface MediaQueryList {
  readonly matches: boolean;
  readonly media: string;
}

// Scroll types
export interface ScrollPosition {
  readonly x: number;
  readonly y: number;
}

export interface ScrollOptions {
  readonly behavior?: ScrollBehavior;
  readonly block?: ScrollLogicalPosition;
  readonly inline?: ScrollLogicalPosition;
}

// Local storage types
export interface StorageData {
  readonly recentQueries: string[];
  readonly preferences: UserPreferences;
  readonly cache: {
    readonly lastUpdate: number;
    readonly data: unknown;
  };
}

export interface UserPreferences {
  readonly theme: ThemeMode;
  readonly defaultLimit: number;
  readonly defaultFormat: 'json' | 'simple';
  readonly advancedVisible: boolean;
  readonly animationsEnabled: boolean;
}

// Accessibility types
export interface A11yConfig {
  readonly announceResults: boolean;
  readonly focusManagement: boolean;
  readonly keyboardNavigation: boolean;
  readonly screenReaderSupport: boolean;
}

export interface AriaAttributes {
  readonly role?: string;
  readonly 'aria-label'?: string;
  readonly 'aria-describedby'?: string;
  readonly 'aria-expanded'?: boolean;
  readonly 'aria-hidden'?: boolean;
  readonly 'aria-live'?: 'polite' | 'assertive' | 'off';
  readonly 'aria-busy'?: boolean;
}
