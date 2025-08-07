/**
 * Type definitions for Medical Product Recommender API
 */

// Base types
export type ProductId = string;
export type CategoryName = string;
export type Currency = 'PLN' | 'EUR' | 'USD';

// Product types
export interface Product {
  readonly id: ProductId;
  readonly name: string;
  readonly category: CategoryName;
  readonly price: number;
  readonly description: string;
}

export interface ProductSummary {
  readonly id: ProductId;
  readonly name: string;
  readonly category: CategoryName;
  readonly price: number;
  readonly description: string; // Truncated for simple format
}

// Recommendation types
export interface RecommendationRequest {
  readonly input: string;
  readonly limit?: number;
  readonly format?: 'json' | 'simple';
}

export interface RecommendationResponse {
  readonly query: string;
  readonly confidence: number;
  readonly count: number;
  readonly products: Product[];
  readonly reasoning?: string;
  readonly meta?: RecommendationMeta;
}

export interface SimpleRecommendationResponse {
  readonly query: string;
  readonly confidence: number;
  readonly count: number;
  readonly products: ProductSummary[];
}

export interface RecommendationMeta {
  readonly total_products_available: number;
  readonly categories_available: number;
  readonly woocommerce_enabled: boolean;
  readonly cache_info?: CacheInfo;
}

// Cache types
export interface CacheInfo {
  readonly products: number;
  readonly age: number;
  readonly is_valid: boolean;
  readonly cache_duration: number;
}

// Products endpoint types
export interface ProductsRequest {
  readonly category?: CategoryName;
  readonly limit?: number;
  readonly offset?: number;
}

export interface ProductsResponse {
  readonly products: ProductSummary[];
  readonly pagination: PaginationInfo;
  readonly meta: ProductsMeta;
}

export interface PaginationInfo {
  readonly total: number;
  readonly limit: number;
  readonly offset: number;
  readonly has_next: boolean;
  readonly has_prev: boolean;
}

export interface ProductsMeta {
  readonly categories_available: CategoryName[];
  readonly woocommerce_enabled: boolean;
}

// Categories endpoint types
export interface CategoryInfo {
  readonly name: CategoryName;
  readonly product_count: number;
}

export interface CategoriesResponse {
  readonly categories: CategoryInfo[];
  readonly total_categories: number;
  readonly total_products: number;
}

// Health check types
export interface HealthCheckResponse {
  readonly status: 'healthy' | 'unhealthy';
  readonly message: string;
  readonly version: string;
  readonly products_count: number;
  readonly woocommerce_enabled: boolean;
  readonly cache_enabled: boolean;
}

// Error types
export interface ApiError {
  readonly error: string;
  readonly code: string;
  readonly message?: string;
  readonly example?: string;
}

export interface ApiErrorResponse {
  readonly error: string;
  readonly code: ApiErrorCode;
  readonly message?: string;
  readonly example?: string;
}

export type ApiErrorCode =
  | 'MISSING_PARAMETER'
  | 'INVALID_PARAMETER'
  | 'NOT_FOUND'
  | 'METHOD_NOT_ALLOWED'
  | 'INTERNAL_ERROR'
  | 'SERVICE_UNAVAILABLE'
  | 'RECOMMENDATION_ERROR'
  | 'PRODUCTS_ERROR'
  | 'CATEGORIES_ERROR';

// HTTP Response wrapper
export interface ApiResponse<T> {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: ApiErrorResponse;
  readonly status: number;
}

// Event types for iframe communication
export interface IframeEvent {
  readonly type: 'medical_recommender';
  readonly event: IframeEventType;
  readonly data?: Record<string, unknown>;
}

export type IframeEventType =
  | 'iframe_loaded'
  | 'search_started'
  | 'search_success'
  | 'search_error'
  | 'results_displayed';

// Configuration types
export interface ApiConfig {
  readonly baseUrl: string;
  readonly timeout: number;
  readonly retries: number;
}

export interface AppConfig {
  readonly api: ApiConfig;
  readonly ui: UIConfig;
  readonly features: FeatureFlags;
}

export interface UIConfig {
  readonly theme: 'light' | 'dark' | 'auto';
  readonly animations: boolean;
  readonly compactMode: boolean;
  readonly defaultLimit: number;
  readonly defaultFormat: 'json' | 'simple';
}

export interface FeatureFlags {
  readonly advancedOptions: boolean;
  readonly analytics: boolean;
  readonly serviceWorker: boolean;
  readonly autoComplete: boolean;
}

// Utility types
export type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

export interface RequestOptions {
  readonly method: RequestMethod;
  readonly headers?: Record<string, string>;
  readonly body?: string;
  readonly timeout?: number;
}

// Type guards
export function isApiError(response: unknown): response is ApiErrorResponse {
  return typeof response === 'object' && response !== null && 'error' in response && 'code' in response;
}

export function isProduct(obj: unknown): obj is Product {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    'category' in obj &&
    'price' in obj &&
    'description' in obj
  );
}

export function isRecommendationResponse(obj: unknown): obj is RecommendationResponse {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'query' in obj &&
    'confidence' in obj &&
    'count' in obj &&
    'products' in obj
  );
}
