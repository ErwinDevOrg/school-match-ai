/**
 * API Service
 *
 * This module provides a configured Axios instance with:
 * - Base URL configuration
 * - Request interceptors (auth headers, logging)
 * - Response interceptors (error handling, toast notifications)
 * - Enhanced logging for debugging
 */

import axios, { AxiosError } from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { useToast } from '@/shared/composables/useToast'

// Initialize toast for error notifications
const toast = useToast()

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')

// Create Axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token and logging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const startTime = Date.now()
    
    // Store start time for duration calculation
    config.metadata = { startTime }
    
    // Get access token from auth store data in localStorage
    try {
      const authData = localStorage.getItem('auth_tokens')
      if (authData) {
        const parsed = JSON.parse(authData)
        const accessToken = parsed.accessToken
        
        if (accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${accessToken}`
        }
      }
    } catch (error) {
      console.error('[API] Error reading auth tokens:', error)
    }
    
    // Enhanced logging in development
    if (import.meta.env.DEV) {
      console.group(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`)
      console.log('Headers:', config.headers)
      if (config.params) {
        console.log('Params:', config.params)
      }
      if (config.data) {
        console.log('Data:', config.data)
      }
      console.groupEnd()
    }
    
    return config
  },
  (error: AxiosError) => {
    console.error('[API] Request setup failed:', error)
    toast.error('Failed to send request')
    return Promise.reject(error)
  }
)

// Add metadata type to Axios config
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: { startTime: number }
  }
}

// Response interceptor - Handle errors and logging
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Calculate request duration
    const duration = response.config.metadata?.startTime
      ? Date.now() - response.config.metadata.startTime
      : 0
    
    // Enhanced logging in development
    if (import.meta.env.DEV) {
      console.group(`✅ [API Response] ${response.status} ${response.config.url}`)
      console.log(`Duration: ${duration}ms`)
      console.log('Response data:', response.data)
      console.log('Response headers:', response.headers)
      console.groupEnd()
    }
    
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    // Calculate request duration if available
    const duration = originalRequest?.metadata?.startTime
      ? Date.now() - originalRequest.metadata.startTime
      : 0
    
    // Enhanced error logging
    if (import.meta.env.DEV) {
      console.group(`❌ [API Error] ${error.response?.status || 'Network Error'} ${originalRequest?.url || 'Unknown URL'}`)
      console.error('Status:', error.response?.status)
      console.error('Message:', error.message)
      console.error('Duration:', `${duration}ms`)
      console.error('Response data:', error.response?.data)
      console.error('Request config:', originalRequest)
      console.groupEnd()
    }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // TODO: Implement token refresh logic after auth store is created
      // const authStore = useAuthStore()
      // const refreshed = await authStore.refreshToken()
      //
      // if (refreshed) {
      //   // Retry original request with new token
      //   return api(originalRequest)
      // }
      
      // Clear tokens and redirect to login
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Show toast notification
      toast.error('Session expired. Please login again.', 5000)
      
      // TODO: Redirect to login after router is available
      // router.push({ name: 'login' })
    }
    
    // Extract error message from response
    const errorData = error.response?.data as any
    const errorMessage =
      errorData?.message ||
      errorData?.error ||
      errorData?.detail ||
      error.message ||
      'An unexpected error occurred'
    
    // Show user-friendly toast notifications based on error type
    if (error.response?.status) {
      switch (error.response.status) {
        case 400:
          toast.error(`Invalid request: ${errorMessage}`, 5000)
          break
        case 401:
          // Already handled above
          break
        case 403:
          toast.error('Access denied. You do not have permission.', 5000)
          break
        case 404:
          toast.error('Resource not found', 4000)
          break
        case 422:
          // Validation error
          toast.error(`Validation error: ${errorMessage}`, 5000)
          break
        case 429:
          toast.error('Too many requests. Please try again later.', 5000)
          break
        case 500:
          toast.error('Server error. Please try again later.', 6000)
          break
        case 503:
          toast.error('Service unavailable. Please try again later.', 6000)
          break
        default:
          // Generic error for other status codes
          if (error.response.status >= 400) {
            toast.error(errorMessage, 5000)
          }
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      toast.error('Request timeout. Please check your connection.', 5000)
    } else if (error.message === 'Network Error') {
      // Network error
      toast.error('Network error. Please check your connection.', 6000)
    } else {
      // Other errors
      toast.error(errorMessage, 5000)
    }
    
    return Promise.reject(error)
  }
)

export default api

