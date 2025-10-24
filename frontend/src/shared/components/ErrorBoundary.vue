<!--
  Error Boundary Component
  
  Catches and displays Vue component errors gracefully.
  Prevents entire app from crashing due to component errors.
  
  Usage:
  <ErrorBoundary>
    <YourComponent />
  </ErrorBoundary>
-->

<script setup lang="ts">
import { ref, onErrorCaptured, computed } from 'vue'
import { useToast } from '@/shared/composables/useToast'

interface ErrorInfo {
  message: string
  stack?: string
  componentName?: string
  timestamp: Date
}

const hasError = ref(false)
const error = ref<ErrorInfo | null>(null)
const errorCount = ref(0)
const toast = useToast()

// Check if we're in development mode
const isDev = computed(() => import.meta.env.DEV)

// Define props
interface Props {
  fallbackMessage?: string
  showDetails?: boolean
  showReload?: boolean
  reportErrors?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  fallbackMessage: 'An error occurred while rendering this component',
  showDetails: true,
  showReload: true,
  reportErrors: true,
})

// Capture errors from child components
onErrorCaptured((err: Error, instance, info) => {
  hasError.value = true
  errorCount.value++
  
  error.value = {
    message: err.message || 'Unknown error',
    stack: err.stack,
    componentName: instance?.$options?.name || instance?.$options?.__name || 'Unknown',
    timestamp: new Date(),
  }

  // Show toast notification for errors
  toast.error(`Component Error: ${err.message}`)

  // Log error details in development
  if (isDev.value) {
    console.error('[ErrorBoundary] Caught error:', {
      message: err.message,
      component: error.value.componentName,
      info,
      stack: err.stack,
    })
  }

  // Report error to monitoring service in production
  if (props.reportErrors && !isDev.value) {
    // TODO: Integrate with error monitoring service (e.g., Sentry)
    // reportErrorToService(err, instance, info)
  }

  // Prevent error from propagating further
  return false
})

// Reset error state and try to render again
const handleReset = () => {
  hasError.value = false
  error.value = null
}

// Reload the entire page
const handleReload = () => {
  window.location.reload()
}

// Copy error details to clipboard
const copyErrorDetails = async () => {
  if (!error.value) return

  const details = `
Error: ${error.value.message}
Component: ${error.value.componentName}
Time: ${error.value.timestamp.toISOString()}
Stack: ${error.value.stack || 'N/A'}
  `.trim()

  try {
    await navigator.clipboard.writeText(details)
    toast.success('Error details copied to clipboard')
  } catch (e) {
    console.error('Failed to copy error details:', e)
    toast.error('Failed to copy error details')
  }
}
</script>

<template>
  <div class="error-boundary">
    <!-- Show error fallback when error is caught -->
    <div v-if="hasError" class="error-fallback">
      <div class="error-icon">⚠️</div>
      
      <h2 class="error-title">Oops! Something went wrong</h2>
      
      <p class="error-message">{{ props.fallbackMessage }}</p>

      <!-- Error details (only in development or when explicitly enabled) -->
      <div v-if="props.showDetails && error" class="error-details">
        <details>
          <summary>Error Details</summary>
          <div class="error-details-content">
            <p><strong>Message:</strong> {{ error.message }}</p>
            <p v-if="error.componentName">
              <strong>Component:</strong> {{ error.componentName }}
            </p>
            <p><strong>Time:</strong> {{ error.timestamp.toLocaleString() }}</p>
            <pre v-if="error.stack" class="error-stack">{{ error.stack }}</pre>
          </div>
        </details>
      </div>

      <!-- Action buttons -->
      <div class="error-actions">
        <button @click="handleReset" class="btn btn-primary">
          Try Again
        </button>
        
        <button v-if="props.showReload" @click="handleReload" class="btn btn-secondary">
          Reload Page
        </button>

        <button v-if="props.showDetails && error" @click="copyErrorDetails" class="btn btn-secondary">
          Copy Details
        </button>
      </div>

      <!-- Error count indicator (for debugging) -->
      <div v-if="isDev && errorCount > 1" class="error-count">
        Error occurred {{ errorCount }} times
      </div>
    </div>

    <!-- Render children when no error -->
    <slot v-else />
  </div>
</template>

<style scoped>
.error-boundary {
  width: 100%;
}

.error-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  min-height: 300px;
  background-color: #fff;
  border: 1px solid #fee;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #dc2626;
  margin: 0 0 1rem 0;
}

.error-message {
  font-size: 1rem;
  color: #6b7280;
  margin: 0 0 2rem 0;
  text-align: center;
  max-width: 500px;
}

.error-details {
  width: 100%;
  max-width: 600px;
  margin: 1.5rem 0;
}

.error-details details {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
}

.error-details summary {
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  user-select: none;
}

.error-details summary:hover {
  color: #111827;
}

.error-details-content {
  margin-top: 1rem;
  font-size: 0.875rem;
}

.error-details-content p {
  margin: 0.5rem 0;
  color: #4b5563;
}

.error-stack {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #1f2937;
  color: #f3f4f6;
  border-radius: 4px;
  font-size: 0.75rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.error-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn:active {
  transform: scale(0.98);
}

.error-count {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 0.875rem;
}
</style>

