/**
 * User Service
 * 
 * API service for user profile management operations.
 */

import api from '@/shared/services/api'
import type {
  PasswordChange,
  UserProfile,
  UserUpdate
} from '../types/user.types'

export const userService = {
  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/api/v1/users/me')
    return response.data
  },

  /**
   * Update current user profile
   */
  async updateProfile(data: UserUpdate): Promise<UserProfile> {
    const response = await api.patch<UserProfile>('/api/v1/users/me', data)
    return response.data
  },

  /**
   * Change user password
   */
  async changePassword(data: PasswordChange): Promise<void> {
    await api.put('/api/v1/users/me/password', data)
  }
}

export default userService

