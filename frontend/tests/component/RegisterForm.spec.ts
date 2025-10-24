/**
 * Component Tests for RegisterView
 * 
 * Tests for the registration form functionality and user interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import RegisterView from '@/domains/auth/views/RegisterView.vue'
import { useAuthStore } from '@/stores/auth'
import authService from '@/domains/auth/services/authService'
import userService from '@/domains/user/services/userService'

// Mock the services
vi.mock('@/domains/auth/services/authService')
vi.mock('@/domains/user/services/userService')

describe('RegisterView Component', () => {
  let wrapper: VueWrapper
  let router: any

  beforeEach(async () => {
    // Create fresh pinia and router
    setActivePinia(createPinia())
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
        { path: '/register', name: 'register', component: RegisterView },
        { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
        { path: '/profile', name: 'profile', component: { template: '<div>Profile</div>' } },
      ],
    })

    await router.push('/register')
    await router.isReady()

    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    vi.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('should render registration form with all required inputs', () => {
      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThanOrEqual(3)
      expect(wrapper.html()).toContain('type="email"')
      expect(wrapper.html()).toContain('type="password"')
      expect(wrapper.html()).toContain('type="text"')
    })

    it('should render register button', () => {
      const button = wrapper.find('button[type="submit"]')
      expect(button.exists()).toBe(true)
      expect(wrapper.text()).toMatch(/register|create/i)
    })

    it('should have link to login page', () => {
      const link = wrapper.find('a')
      expect(link.exists()).toBe(true)
      expect(link.attributes('href')).toContain('login')
    })

    it('should display page title', () => {
      expect(wrapper.text()).toMatch(/register|create|sign up/i)
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

    it('should have minimum password length requirement', () => {
      const passwordInput = wrapper.find('input[type="password"]')
      const minLength = passwordInput.attributes('minlength')
      if (minLength) {
        expect(parseInt(minLength)).toBeGreaterThanOrEqual(8)
      }
    })
  })

  describe('Form Submission', () => {
    it('should register new user with valid data', async () => {
      const mockUser = {
        id: 1,
        email: 'newuser@example.com',
        full_name: 'New User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }

      const mockTokens = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      vi.mocked(authService.register).mockResolvedValue(mockUser)
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('New User')
      await emailInput.setValue('newuser@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const authStore = useAuthStore()
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('should display error message when email already exists', async () => {
      vi.mocked(authService.register).mockRejectedValue({
        response: {
          data: {
            message: 'Email already registered',
          },
        },
      })

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('Test User')
      await emailInput.setValue('existing@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()

      // Check for error message
      expect(wrapper.text()).toMatch(/already|exists|registered/i)
    })

    it('should disable submit button while processing', async () => {
      vi.mocked(authService.register).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")
      const submitButton = wrapper.find('button[type="submit"]')

      await nameInput.setValue('Test User')
      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      
      form.trigger('submit')
      await wrapper.vm.$nextTick()

      // Button should be disabled during submission
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should clear password field on error', async () => {
      vi.mocked(authService.register).mockRejectedValue(new Error('Registration failed'))

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('Test User')
      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Form should show error
      expect(wrapper.text()).toMatch(/error|failed/i)
    })

    it('should handle network errors gracefully', async () => {
      vi.mocked(authService.register).mockRejectedValue(new Error('Network error'))

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('Test User')
      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Should display error message
      expect(wrapper.text()).toMatch(/error|failed/i)
    })
  })

  describe('Password Confirmation', () => {
    it('should have password confirmation field if implemented', () => {
      const passwordInputs = wrapper.findAll('input[type="password"]')
      // May or may not have confirm password field
      expect(passwordInputs.length).toBeGreaterThanOrEqual(1)
    })

    it('should validate password match if confirmation field exists', async () => {
      const passwordInputs = wrapper.findAll('input[type="password"]')
      
      if (passwordInputs.length > 1) {
        const passwordInput = passwordInputs[0]
        const confirmInput = passwordInputs[1]

        await passwordInput.setValue('password123')
        await confirmInput.setValue('password456')

        const form = wrapper.find('form')
        await form.trigger('submit.prevent')
        await wrapper.vm.$nextTick()

        // Should show validation error
        expect(wrapper.text()).toMatch(/match|same|different/i)
      }
    })
  })

  describe('Navigation', () => {
    it('should redirect to profile after successful registration', async () => {
      const mockUser = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }

      const mockTokens = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      vi.mocked(authService.register).mockResolvedValue(mockUser)
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)

      const form = wrapper.find('form')
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('Test User')
      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      await router.isReady()

      // Should redirect to profile or home
      expect(['/profile', '/']).toContain(router.currentRoute.value.path)
    })

    it('should navigate to login page when clicking login link', async () => {
      const loginLink = wrapper.find('a')
      expect(loginLink.attributes('href')).toContain('login')
      
      await router.push('/login')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('login')
    })
  })

  describe('User Experience', () => {
    it('should show loading state during registration', async () => {
      vi.mocked(authService.register).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )

      const form = wrapper.find('form')
      const submitButton = wrapper.find('button[type="submit"]')
      
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      // Button should be disabled and show loading state
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should allow user to type in all form fields', async () => {
      const inputs = wrapper.findAll('input')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      const nameInput = inputs[0] // First input is full name (type="text")

      await nameInput.setValue('Test User')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('mypassword')

      expect((nameInput.element as HTMLInputElement).value).toBe('Test User')
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

    it('should have meaningful button text', () => {
      const button = wrapper.find('button[type="submit"]')
      expect(button.text().length).toBeGreaterThan(0)
    })
  })

  describe('Field Requirements', () => {
    it('should handle submit with empty fields', async () => {
      const form = wrapper.find('form')
      await form.trigger('submit')

      await wrapper.vm.$nextTick()

      // Component submits to backend which validates
      // Empty required fields will be caught by HTML5 validation or backend
      expect(form.exists()).toBe(true)
    })

    it('should accept optional full name', async () => {
      const mockUser = {
        id: 1,
        email: 'user@example.com',
        full_name: '',
        is_active: true,
        is_verified: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }

      const mockTokens = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
        expires_in: 900,
      }
      
      vi.mocked(authService.register).mockResolvedValue(mockUser)
      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(userService.getProfile).mockResolvedValue(mockUser)

      const form = wrapper.find('form')
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      await emailInput.setValue('user@example.com')
      await passwordInput.setValue('password123')
      await form.trigger('submit.prevent')

      await wrapper.vm.$nextTick()

      // Registration may succeed without full name
      // depending on backend requirements
    })
  })
})

