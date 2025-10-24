/**
 * Common API Types
 *
 * This module defines shared TypeScript types for API interactions.
 */

/**
 * Standard API error response
 */
export interface ApiError {
  error: string
  message: string
  details?: Record<string, any>
}

/**
 * Standard API success response
 */
export interface ApiResponse<T = any> {
  data: T
  message?: string
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_prev: boolean
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  version: string
}

/**
 * Generic ID parameter
 */
export type ID = number | string

/**
 * Timestamp strings (ISO 8601)
 */
export type Timestamp = string

/**
 * Generic query parameters for list endpoints
 */
export interface QueryParams {
  page?: number
  page_size?: number
  sort?: string
  order?: 'asc' | 'desc'
  search?: string
}

