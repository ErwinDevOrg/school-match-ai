/**
 * User Domain TypeScript Types
 * 
 * Type definitions for user profile management data structures.
 */

export interface UserProfile {
  id: number
  email: string
  full_name?: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  last_login_at?: string | null
}

export interface UserUpdate {
  email?: string
  full_name?: string
}

export interface PasswordChange {
  current_password: string
  new_password: string
}

