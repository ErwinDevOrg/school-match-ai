/**
 * Unit Tests for User Composables
 * 
 * Tests for useUser composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUser } from '@/domains/user/composables/useUser'
import userService from '@/domains/user/services/userService'
import { useAuthStore } from '@/stores/auth'

// Mock the user service
vi.mock('@/domains/user/services/userService')

describe('useUser Composable', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('State', () => {
    it('should initialize with default state', () => {
      const { loading, error } = useUser()
      
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
    })
  })

  describe('getProfile', () => {
    it('should get user profile successfully', async () => {
      const { getProfile, loading, error } = useUser()
      
      const mockProfile = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      
      vi.mocked(userService.getProfile).mockResolvedValue(mockProfile)
      
      const result = await getProfile()
      
      expect(result).toEqual(mockProfile)
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(userService.getProfile).toHaveBeenCalled()
    })

    it('should set loading state during profile fetch', async () => {
      const { getProfile, loading } = useUser()
      
      let loadingDuringFetch = false
      
      vi.mocked(userService.getProfile).mockImplementation(async () => {
        loadingDuringFetch = loading.value
        return Promise.resolve({
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          is_active: true,
          is_verified: false,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        })
      })
      
      await getProfile()
      
      expect(loadingDuringFetch).toBe(true)
      expect(loading.value).toBe(false)
    })

    it('should handle profile fetch errors', async () => {
      const { getProfile, loading, error } = useUser()
      
      const errorResponse = {
        response: {
          data: {
            message: 'Failed to load profile',
          },
        },
      }
      
      vi.mocked(userService.getProfile).mockRejectedValue(errorResponse)
      
      await expect(getProfile()).rejects.toThrow()
      
      expect(loading.value).toBe(false)
      expect(error.value).toBe('Failed to load profile')
    })

    it('should handle generic errors', async () => {
      const { getProfile, error } = useUser()
      
      vi.mocked(userService.getProfile).mockRejectedValue(new Error('Network error'))
      
      await expect(getProfile()).rejects.toThrow()
      
      expect(error.value).toBe('Failed to load profile')
    })
  })

  describe('updateProfile', () => {
    it('should update profile successfully', async () => {
      const { updateProfile, loading, error } = useUser()
      const authStore = useAuthStore()
      
      const mockUpdatedProfile = {
        id: 1,
        email: 'updated@example.com',
        full_name: 'Updated Name',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }
      
      vi.mocked(userService.updateProfile).mockResolvedValue(mockUpdatedProfile)
      
      // Mock loadUserProfile method
      const loadProfileSpy = vi.spyOn(authStore, 'loadUserProfile').mockResolvedValue()
      
      const updateData = {
        email: 'updated@example.com',
        full_name: 'Updated Name',
      }
      
      const result = await updateProfile(updateData)
      
      expect(result).toEqual(mockUpdatedProfile)
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(userService.updateProfile).toHaveBeenCalledWith(updateData)
      expect(loadProfileSpy).toHaveBeenCalled()
    })

    it('should handle update profile errors', async () => {
      const { updateProfile, error } = useUser()
      
      const errorResponse = {
        response: {
          data: {
            message: 'Email already in use',
          },
        },
      }
      
      vi.mocked(userService.updateProfile).mockRejectedValue(errorResponse)
      
      await expect(updateProfile({ email: 'existing@example.com' })).rejects.toThrow()
      
      expect(error.value).toBe('Email already in use')
    })
  })

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const { changePassword, loading, error } = useUser()
      
      vi.mocked(userService.changePassword).mockResolvedValue(undefined)
      
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
      }
      
      await changePassword(passwordData)
      
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(userService.changePassword).toHaveBeenCalledWith(passwordData)
    })

    it('should handle password change errors', async () => {
      const { changePassword, error } = useUser()
      
      const errorResponse = {
        response: {
          data: {
            message: 'Current password is incorrect',
          },
        },
      }
      
      vi.mocked(userService.changePassword).mockRejectedValue(errorResponse)
      
      await expect(
        changePassword({
          current_password: 'wrongpassword',
          new_password: 'newpassword123',
        })
      ).rejects.toThrow()
      
      expect(error.value).toBe('Current password is incorrect')
    })

    it('should set loading state during password change', async () => {
      const { changePassword, loading } = useUser()
      
      let loadingDuringChange = false
      
      vi.mocked(userService.changePassword).mockImplementation(async () => {
        loadingDuringChange = loading.value
        return Promise.resolve()
      })
      
      await changePassword({
        current_password: 'oldpassword',
        new_password: 'newpassword123',
      })
      
      expect(loadingDuringChange).toBe(true)
      expect(loading.value).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should clear previous errors on new operations', async () => {
      const { getProfile, error } = useUser()
      
      // First call - error
      vi.mocked(userService.getProfile).mockRejectedValueOnce(new Error('Error 1'))
      
      await expect(getProfile()).rejects.toThrow()
      expect(error.value).toBeTruthy()
      
      // Second call - success
      vi.mocked(userService.getProfile).mockResolvedValueOnce({
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      })
      
      await getProfile()
      expect(error.value).toBeNull()
    })
  })

  describe('Loading State Management', () => {
    it('should reset loading state after operation completes', async () => {
      const { getProfile, loading } = useUser()
      
      vi.mocked(userService.getProfile).mockResolvedValue({
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      })
      
      expect(loading.value).toBe(false)
      
      const promise = getProfile()
      // Don't check loading here as it might already be done
      
      await promise
      expect(loading.value).toBe(false)
    })

    it('should reset loading state after error', async () => {
      const { getProfile, loading } = useUser()
      
      vi.mocked(userService.getProfile).mockRejectedValue(new Error('Error'))
      
      expect(loading.value).toBe(false)
      
      try {
        await getProfile()
      } catch {
        // Expected error
      }
      
      expect(loading.value).toBe(false)
    })
  })
})

