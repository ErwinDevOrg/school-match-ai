/**
 * Vite Configuration
 *
 * Configuration for Vite build tool including:
 * - Vue plugin
 * - Development server proxy for backend API
 * - Path aliases
 * - Build optimizations
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  
  server: {
    port: 5173,
    host: true, // Listen on all addresses (useful for Docker/network access)
    strictPort: false, // Try next port if 5173 is taken
    
    // HMR (Hot Module Replacement) configuration for fast development
    hmr: {
      overlay: true, // Show error overlay on the page
      clientPort: 5173,
    },
    
    // Watch options for faster file change detection
    watch: {
      usePolling: false, // Use native file watchers (faster)
      interval: 100, // Polling interval if usePolling is true
    },
    
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy other backend endpoints
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/docs': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  
  build: {
    // Build optimizations
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
    
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          axios: ['axios'],
        },
      },
    },
  },
})

