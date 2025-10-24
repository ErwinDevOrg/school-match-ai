/**
 * Unit Tests for Authentication Store and Composables
 * 
 * Tests for Pinia auth store and useAuth composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/domains/auth/composables/useAuth'
import authService from '@/domains/auth/services/authService'
import userService from '@/domains/user/services/userService'

// Mock the services
vi.mock('@/domains/auth/services/authService')
vi.mock('@/domains/user/services/userService')

describe('Auth Store', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia())
    // Clear localStorage
    localStorage.clear()
    // Reset mocks
    vi.clearAllMocks()
  })

  describe('State Management', () => {
    it('should initialize with null user and tokens', () => {
      const authStore = useAuthStore()
      
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBeNull()
      expect(authStore.refreshToken).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('should set authenticated when user and token exist', () => {
      const authStore = useAuthStore()
      
      authStore.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      authStore.accessToken = 'test-access-token'
      
      expect(authStore.isAuthenticated).toBe(true)
    })
  })

  describe('Registration', () => {
    it('should register a new user successfully', async () => {
      const authStore = useAuthStore()
      
      const mockTokens = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      const mockUser = {
        id: 1,
        email: 'newuser@example.com',
        full_name: 'New User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      
      vi.mocked(authService.register).mockResolvedValue(mockUser)
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)
      
      await authStore.register({
        email: 'newuser@example.com',
        password: 'password123',
        full_name: 'New User',
      })
      
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.user?.email).toBe('newuser@example.com')
      expect(authStore.accessToken).toBe('new-access-token')
    })

    it('should handle registration errors', async () => {
      const authStore = useAuthStore()
      
      vi.mocked(authService.register).mockRejectedValue(
        new Error('Email already exists')
      )
      
      await expect(
        authStore.register({
          email: 'existing@example.com',
          password: 'password123',
        })
      ).rejects.toThrow('Email already exists')
      
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Login', () => {
    it('should login successfully', async () => {
      const authStore = useAuthStore()
      
      const mockTokens = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      const mockUser = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)
      
      await authStore.login({
        email: 'user@example.com',
        password: 'password123',
      })
      
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.user?.email).toBe('user@example.com')
      expect(authStore.accessToken).toBe('access-token')
      expect(authStore.refreshToken).toBe('refresh-token')
    })

    it('should handle login errors', async () => {
      const authStore = useAuthStore()
      
      vi.mocked(authService.login).mockRejectedValue(
        new Error('Invalid credentials')
      )
      
      await expect(
        authStore.login({
          email: 'user@example.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials')
      
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Logout', () => {
    it('should logout and clear state', async () => {
      const authStore = useAuthStore()
      
      // Setup authenticated state
      authStore.user = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      authStore.accessToken = 'access-token'
      authStore.refreshToken = 'refresh-token'
      
      vi.mocked(authService.logout).mockResolvedValue(undefined)
      
      await authStore.logout()
      
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBeNull()
      expect(authStore.refreshToken).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('should clear state even if logout request fails', async () => {
      const authStore = useAuthStore()
      
      authStore.user = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      authStore.accessToken = 'access-token'
      authStore.refreshToken = 'refresh-token'
      
      vi.mocked(authService.logout).mockRejectedValue(new Error('Network error'))
      
      await authStore.logout()
      
      // State should still be cleared
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Token Persistence', () => {
    it('should persist tokens to localStorage', async () => {
      const authStore = useAuthStore()
      
      const mockTokens = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      const mockUser = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)
      
      await authStore.login({
        email: 'user@example.com',
        password: 'password123',
      })
      
      const storedData = localStorage.getItem('auth_tokens')
      expect(storedData).toBeTruthy()
      
      const parsed = JSON.parse(storedData!)
      expect(parsed.accessToken).toBe('access-token')
      expect(parsed.refreshToken).toBe('refresh-token')
    })

    it('should clear localStorage on logout', async () => {
      const authStore = useAuthStore()
      
      localStorage.setItem('auth_tokens', JSON.stringify({
        accessToken: 'token',
        refreshToken: 'refresh',
        expiresAt: Date.now() + 900000,
      }))
      
      vi.mocked(authService.logout).mockResolvedValue(undefined)
      
      await authStore.logout()
      
      expect(localStorage.getItem('auth_tokens')).toBeNull()
    })
  })
})

describe('useAuth Composable', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should provide auth state', () => {
    const { isAuthenticated, user } = useAuth()
    
    expect(isAuthenticated.value).toBe(false)
    expect(user.value).toBeNull()
  })

  it('should provide login function', () => {
    const { login } = useAuth()
    
    expect(typeof login).toBe('function')
  })

  it('should provide register function', () => {
    const { register } = useAuth()
    
    expect(typeof register).toBe('function')
  })

  it('should provide logout function', () => {
    const { logout } = useAuth()
    
    expect(typeof logout).toBe('function')
  })

  it('should call store login method', async () => {
    const { login } = useAuth()
    const authStore = useAuthStore()
    
    const spy = vi.spyOn(authStore, 'login')
    
    const mockTokens = {
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'bearer',
      expires_in: 900,
    }
    
    const mockUser = {
      id: 1,
      email: 'user@example.com',
      full_name: 'Test User',
      is_active: true,
      is_verified: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    }
    
    vi.mocked(authService.login).mockResolvedValue(mockTokens)
    vi.mocked(userService.getProfile).mockResolvedValue(mockUser)
    
    await login({ email: 'user@example.com', password: 'password' })
    
    expect(spy).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password',
    })
  })
})

