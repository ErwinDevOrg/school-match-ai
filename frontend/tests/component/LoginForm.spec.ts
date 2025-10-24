/**
 * Component Tests for LoginView
 * 
 * Tests for the login form functionality and user interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/domains/auth/views/LoginView.vue'
import { useAuthStore } from '@/stores/auth'
import authService from '@/domains/auth/services/authService'
import userService from '@/domains/user/services/userService'

// Mock the services
vi.mock('@/domains/auth/services/authService')
vi.mock('@/domains/user/services/userService')

describe('LoginView Component', () => {
  let wrapper: VueWrapper
  let router: any

  beforeEach(async () => {
    // Create fresh pinia and router
    setActivePinia(createPinia())
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
        { path: '/login', name: 'login', component: LoginView },
        { path: '/profile', name: 'profile', component: { template: '<div>Profile</div>' } },
      ],
    })

    await router.push('/login')
    await router.isReady()

    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    vi.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('should render login form with email and password inputs', () => {
      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThanOrEqual(2)
      expect(wrapper.html()).toContain('type="email"')
      expect(wrapper.html()).toContain('type="password"')
    })

    it('should render login button', () => {
      const button = wrapper.find('button[type="submit"]')
      expect(button.exists()).toBe(true)
      expect(wrapper.text()).toContain('Login')
    })

    it('should have link to registration page', () => {
      const link = wrapper.find('a')
      expect(link.exists()).toBe(true)
      expect(link.attributes('href')).toContain('register')
    })

    it('should display page title', () => {
      expect(wrapper.text()).toContain('Login')
    })
  })

  describe('Form Validation', () => {
    it('should require email field', async () => {
      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.attributes('required')).toBeDefined()
    })

    it('should require password field', async () => {
      const passwordInput = wrapper.find('input[type="password"]')
      expect(passwordInput.attributes('required')).toBeDefined()
    })

    it('should validate email format', async () => {
      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.attributes('type')).toBe('email')
    })
  })

  describe('Form Submission', () => {
    it('should call login on form submit with valid credentials', async () => {
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

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      // Wait for async operations
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const authStore = useAuthStore()
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('should display error message on login failure', async () => {
      vi.mocked(authService.login).mockRejectedValue({
        response: {
          data: {
            message: 'Invalid credentials',
          },
        },
      })

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('wrongpassword')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Check for error message in the component
      expect(wrapper.text()).toMatch(/invalid|error|failed|credentials/i)
    })

    it('should disable submit button while loading', async () => {
      vi.mocked(authService.login).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const submitButton = wrapper.find('button[type="submit"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      
      form.trigger('submit')
      await wrapper.vm.$nextTick()

      // Button should be disabled during submission
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should keep form values on error', async () => {
      vi.mocked(authService.login).mockRejectedValue(new Error('Login failed'))

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Email should still be there for retry
      expect((emailInput.element as HTMLInputElement).value).toBe('user@example.com')
    })
  })

  describe('Navigation', () => {
    it('should redirect to profile after successful login', async () => {
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

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      await router.isReady()

      // Should redirect to profile or intended page
      expect(['/profile', '/']).toContain(router.currentRoute.value.path)
    })
  })

  describe('User Experience', () => {
    it('should show loading state during login', async () => {
      vi.mocked(authService.login).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )

      const form = wrapper.find('form')
      const submitButton = wrapper.find('button[type="submit"]')
      
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      // Button should be disabled and show loading state
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should allow user to type in form fields', async () => {
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('mypassword')

      expect((emailInput.element as HTMLInputElement).value).toBe('test@example.com')
      expect((passwordInput.element as HTMLInputElement).value).toBe('mypassword')
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for inputs', () => {
      const labels = wrapper.findAll('label')
      expect(labels.length).toBeGreaterThan(0)
    })

    it('should have proper form structure', () => {
      const form = wrapper.find('form')
      expect(form.exists()).toBe(true)
    })
  })
})

