/**
 * useUser Composable
 * 
 * Provides user profile management functionality to components.
 */

import { ref } from 'vue'
import userService from '../services/userService'
import { useAuthStore } from '@/stores/auth'
import type { PasswordChange, UserProfile, UserUpdate } from '../types/user.types'

export function useUser() {
  const authStore = useAuthStore()
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function getProfile(): Promise<UserProfile | null> {
    loading.value = true
    error.value = null
    
    try {
      const profile = await userService.getProfile()
      return profile
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: UserUpdate): Promise<UserProfile | null> {
    loading.value = true
    error.value = null
    
    try {
      const updatedProfile = await userService.updateProfile(data)
      
      // Update user in auth store
      await authStore.loadUserProfile()
      
      return updatedProfile
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changePassword(data: PasswordChange): Promise<void> {
    loading.value = true
    error.value = null
    
    try {
      await userService.changePassword(data)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to change password'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    loading,
    error,
    
    // Actions
    getProfile,
    updateProfile,
    changePassword
  }
}

export default useUser

