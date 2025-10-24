/**
 * Toast Notification Composable
 *
 * Provides a reactive toast notification system with:
 * - Success, error, warning, and info toast types
 * - Auto-dismiss with configurable duration
 * - Manual dismiss capability
 * - Stacking multiple toasts
 * - Position configuration
 */

import { ref, computed } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'
export type ToastPosition = 'top-right' | 'top-center' | 'top-left' | 'bottom-right' | 'bottom-center' | 'bottom-left'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration: number
  timestamp: number
}

// Global state for toasts (shared across all instances)
const toasts = ref<Toast[]>([])
let toastIdCounter = 0

/**
 * Toast notification composable
 *
 * Usage:
 * ```ts
 * const toast = useToast()
 * toast.success('Operation successful!')
 * toast.error('An error occurred', 5000)
 * ```
 */
export function useToast() {
  /**
   * Add a toast notification
   */
  const addToast = (type: ToastType, message: string, duration: number = 4000): string => {
    const id = `toast-${++toastIdCounter}-${Date.now()}`
    const toast: Toast = {
      id,
      type,
      message,
      duration,
      timestamp: Date.now(),
    }

    toasts.value.push(toast)

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  /**
   * Remove a specific toast
   */
  const removeToast = (id: string) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * Clear all toasts
   */
  const clearAll = () => {
    toasts.value = []
  }

  /**
   * Show success toast
   */
  const success = (message: string, duration?: number): string => {
    return addToast('success', message, duration)
  }

  /**
   * Show error toast
   */
  const error = (message: string, duration?: number): string => {
    // Error toasts stay longer by default
    return addToast('error', message, duration ?? 6000)
  }

  /**
   * Show warning toast
   */
  const warning = (message: string, duration?: number): string => {
    return addToast('warning', message, duration)
  }

  /**
   * Show info toast
   */
  const info = (message: string, duration?: number): string => {
    return addToast('info', message, duration)
  }

  /**
   * All active toasts (reactive)
   */
  const activeToasts = computed(() => toasts.value)

  /**
   * Check if there are any active toasts
   */
  const hasToasts = computed(() => toasts.value.length > 0)

  return {
    // State
    toasts: activeToasts,
    hasToasts,

    // Methods
    success,
    error,
    warning,
    info,
    remove: removeToast,
    clearAll,
  }
}

/**
 * Toast configuration
 */
export interface ToastConfig {
  position: ToastPosition
  maxToasts: number
  defaultDuration: number
}

const defaultConfig: ToastConfig = {
  position: 'top-right',
  maxToasts: 5,
  defaultDuration: 4000,
}

const config = ref<ToastConfig>({ ...defaultConfig })

/**
 * Configure toast defaults
 */
export function configureToast(options: Partial<ToastConfig>) {
  config.value = { ...config.value, ...options }
}

/**
 * Get current toast configuration
 */
export function getToastConfig() {
  return computed(() => config.value)
}

