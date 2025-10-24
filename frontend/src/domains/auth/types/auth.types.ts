/**
 * Authentication Domain TypeScript Types
 * 
 * Type definitions for authentication-related data structures.
 */

export interface User {
  id: number
  email: string
  full_name?: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  last_login_at?: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegistrationData {
  email: string
  password: string
  full_name?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface TokenRefreshRequest {
  refresh_token: string
}

export interface LogoutRequest {
  refresh_token?: string
}

