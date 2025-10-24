/**
 * Authentication Service
 * 
 * API service for authentication operations (register, login, token refresh, logout).
 */

import api from '@/shared/services/api'
import type {
  LoginCredentials,
  RegistrationData,
  TokenResponse,
  User
} from '../types/auth.types'

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegistrationData): Promise<User> {
    const response = await api.post<User>('/api/v1/auth/register', data)
    return response.data
  },

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/login', credentials)
    return response.data
  },

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  /**
   * Logout and revoke refresh token
   */
  async logout(refreshToken?: string): Promise<void> {
    await api.post('/api/v1/auth/logout', {
      refresh_token: refreshToken
    })
  }
}

export default authService

