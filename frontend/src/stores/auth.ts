/**
 * Authentication Store
 * 
 * Pinia store for managing authentication state, tokens, and user session.
 * Includes localStorage persistence and automatic token refresh.
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import authService from '@/domains/auth/services/authService'
import userService from '@/domains/user/services/userService'
import type {
  LoginCredentials,
  RegistrationData,
  TokenResponse,
  User
} from '@/domains/auth/types/auth.types'

const TOKEN_STORAGE_KEY = 'auth_tokens'
const REFRESH_BUFFER_SECONDS = 60 // Refresh 60 seconds before expiration

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const tokenExpiresAt = ref<number | null>(null)
  const refreshTimerId = ref<number | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)

  // Actions
  async function register(data: RegistrationData): Promise<void> {
    try {
      // Register user (returns user, but we need to login to get tokens)
      await authService.register(data)
      
      // Login after registration
      await login({
        email: data.email,
        password: data.password
      })
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    try {
      // Login and get tokens
      const tokens = await authService.login(credentials)
      
      // Set tokens
      setTokens(tokens)
      
      // Load user profile
      await loadUserProfile()
      
      // Setup automatic token refresh
      setupTokenRefresh()
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  async function logout(): Promise<void> {
    try {
      // Revoke refresh token on server
      if (refreshToken.value) {
        await authService.logout(refreshToken.value)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local state regardless of server response
      clearAuth()
    }
  }

  async function refreshAccessToken(): Promise<void> {
    if (!refreshToken.value) {
      clearAuth()
      throw new Error('No refresh token available')
    }

    try {
      const tokens = await authService.refreshToken(refreshToken.value)
      setTokens(tokens)
      setupTokenRefresh()
    } catch (error) {
      console.error('Token refresh error:', error)
      clearAuth()
      throw error
    }
  }

  async function loadUserProfile(): Promise<void> {
    try {
      const profile = await userService.getProfile()
      user.value = profile
    } catch (error) {
      console.error('Load profile error:', error)
      throw error
    }
  }

  function setTokens(tokens: TokenResponse): void {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    
    // Calculate expiration time
    const now = Date.now()
    tokenExpiresAt.value = now + (tokens.expires_in * 1000)
    
    // Persist to localStorage
    persistTokens()
  }

  function persistTokens(): void {
    if (accessToken.value && refreshToken.value && tokenExpiresAt.value) {
      const data = {
        accessToken: accessToken.value,
        refreshToken: refreshToken.value,
        expiresAt: tokenExpiresAt.value
      }
      localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(data))
    }
  }

  function loadPersistedTokens(): void {
    try {
      const data = localStorage.getItem(TOKEN_STORAGE_KEY)
      if (data) {
        const parsed = JSON.parse(data)
        accessToken.value = parsed.accessToken
        refreshToken.value = parsed.refreshToken
        tokenExpiresAt.value = parsed.expiresAt
        
        // Check if token is expired
        const now = Date.now()
        if (tokenExpiresAt.value && tokenExpiresAt.value > now) {
          // Token still valid, load user profile and setup refresh
          loadUserProfile()
            .then(() => {
              setupTokenRefresh()
            })
            .catch((error) => {
              console.warn('Failed to load user profile on initialization:', error)
              // Don't clear auth immediately - let the user try to use the app
              // If token is truly invalid, API calls will fail and trigger logout
            })
        } else {
          // Token expired, clear auth
          clearAuth()
        }
      }
    } catch (error) {
      console.error('Error loading persisted tokens:', error)
      clearAuth()
    }
  }

  function setupTokenRefresh(): void {
    // Clear existing timer
    if (refreshTimerId.value) {
      clearTimeout(refreshTimerId.value)
    }

    if (!tokenExpiresAt.value) return

    const now = Date.now()
    const timeUntilRefresh = tokenExpiresAt.value - now - (REFRESH_BUFFER_SECONDS * 1000)

    if (timeUntilRefresh > 0) {
      refreshTimerId.value = window.setTimeout(() => {
        refreshAccessToken().catch(() => {
          // If refresh fails, user will need to login again
          clearAuth()
        })
      }, timeUntilRefresh)
    } else {
      // Token about to expire or already expired, refresh now
      refreshAccessToken().catch(() => {
        clearAuth()
      })
    }
  }

  function clearAuth(): void {
    // Clear state
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    tokenExpiresAt.value = null
    
    // Clear timer
    if (refreshTimerId.value) {
      clearTimeout(refreshTimerId.value)
      refreshTimerId.value = null
    }
    
    // Clear localStorage
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }

  // Initialize: Load persisted tokens on store creation
  loadPersistedTokens()

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    
    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    loadUserProfile,
    clearAuth
  }
})

export default useAuthStore

