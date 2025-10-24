/**
 * Vue Router Configuration
 *
 * This module configures Vue Router with:
 * - Route definitions
 * - Navigation guards for authentication
 * - Route metadata
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Define routes
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/domains/auth/views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      guest: true, // Only accessible when not logged in
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/domains/auth/views/RegisterView.vue'),
    meta: {
      requiresAuth: false,
      guest: true, // Only accessible when not logged in
    },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/domains/user/views/ProfileView.vue'),
    meta: {
      requiresAuth: true, // Requires authentication
    },
  },
]

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  
  // Check if route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  // Check if route is guest-only (login/register pages)
  const guestOnly = to.matched.some(record => record.meta.guest)
  
  if (requiresAuth && !isAuthenticated) {
    // Redirect to login if not authenticated
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (guestOnly && isAuthenticated) {
    // Redirect to profile if already authenticated and trying to access guest-only pages
    next({ name: 'profile' })
  } else {
    // Allow navigation
    next()
  }
})

export default router

