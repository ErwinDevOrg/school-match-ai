/**
 * Vue Application Entry Point
 *
 * This module initializes the Vue 3 application with:
 * - Pinia state management
 * - Vue Router
 * - Global plugins and configurations
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './style.css'

// Create Vue app
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)

// Mount app
app.mount('#app')

