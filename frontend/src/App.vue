<template>
  <div id="app">
    <!-- Global toast notifications -->
    <ToastContainer />
    
    <!-- Error boundary for route components -->
    <ErrorBoundary>
      <div v-if="error" class="error-message">
        <h2>Error Loading App</h2>
        <p>{{ error }}</p>
      </div>
      <router-view v-else />
    </ErrorBoundary>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import ToastContainer from '@/shared/components/ToastContainer.vue'
import ErrorBoundary from '@/shared/components/ErrorBoundary.vue'

/**
 * App Root Component
 *
 * This is the main application component that contains the router-view.
 * Includes global components:
 * - ToastContainer: Display toast notifications
 * - ErrorBoundary: Catch and display component errors
 */

const error = ref<string | null>(null)

onErrorCaptured((err) => {
  console.error('Vue Error Captured:', err)
  error.value = err.message || String(err)
  return false
})
</script>

<style scoped>
#app {
  width: 100%;
  min-height: 100vh;
}

.error-message {
  padding: 2rem;
  margin: 2rem;
  background-color: #fee2e2;
  border: 2px solid #ef4444;
  border-radius: 0.5rem;
  color: #991b1b;
}

.error-message h2 {
  margin-bottom: 1rem;
  color: #7f1d1d;
}
</style>

