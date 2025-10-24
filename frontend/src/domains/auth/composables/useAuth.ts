/**
 * useAuth Composable
 * 
 * Provides authentication functionality and state to components.
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials, RegistrationData } from '../types/auth.types'

export function useAuth() {
  const authStore = useAuthStore()

  // Computed properties
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)

  // Actions
  async function login(credentials: LoginCredentials): Promise<void> {
    await authStore.login(credentials)
  }

  async function register(data: RegistrationData): Promise<void> {
    await authStore.register(data)
  }

  async function logout(): Promise<void> {
    await authStore.logout()
  }

  async function refreshToken(): Promise<void> {
    await authStore.refreshAccessToken()
  }

  return {
    // State
    isAuthenticated,
    user,
    
    // Actions
    login,
    register,
    logout,
    refreshToken
  }
}

export default useAuth

