<!--
  Toast Container Component
  
  Displays toast notifications in the UI.
  Place this component in App.vue to show toasts globally.
  
  Usage in App.vue:
  <ToastContainer />
-->

<script setup lang="ts">
import { useToast } from '@/shared/composables/useToast'
import type { Toast } from '@/shared/composables/useToast'

const toast = useToast()

// Get icon for toast type
const getIcon = (type: Toast['type']): string => {
  switch (type) {
    case 'success':
      return '✓'
    case 'error':
      return '✕'
    case 'warning':
      return '⚠'
    case 'info':
      return 'ℹ'
    default:
      return '•'
  }
}

// Get color class for toast type
const getColorClass = (type: Toast['type']): string => {
  switch (type) {
    case 'success':
      return 'toast-success'
    case 'error':
      return 'toast-error'
    case 'warning':
      return 'toast-warning'
    case 'info':
      return 'toast-info'
    default:
      return 'toast-info'
  }
}
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="item in toast.toasts.value"
        :key="item.id"
        :class="['toast', getColorClass(item.type)]"
        @click="toast.remove(item.id)"
      >
        <div class="toast-icon">{{ getIcon(item.type) }}</div>
        <div class="toast-message">{{ item.message }}</div>
        <button
          class="toast-close"
          @click.stop="toast.remove(item.id)"
          aria-label="Close"
        >
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 300px;
  max-width: 400px;
}

.toast:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.toast-icon {
  font-size: 1.25rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #1f2937;
  word-break: break-word;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color 0.2s;
}

.toast-close:hover {
  color: #4b5563;
}

/* Toast type colors */
.toast-success {
  border-left-color: #10b981;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-error {
  border-left-color: #ef4444;
}

.toast-error .toast-icon {
  color: #ef4444;
}

.toast-warning {
  border-left-color: #f59e0b;
}

.toast-warning .toast-icon {
  color: #f59e0b;
}

.toast-info {
  border-left-color: #3b82f6;
}

.toast-info .toast-icon {
  color: #3b82f6;
}

/* Toast animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Responsive design */
@media (max-width: 640px) {
  .toast-container {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
    max-width: none;
  }

  .toast {
    min-width: auto;
    max-width: none;
  }
}
</style>

