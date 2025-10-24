/**
 * End-to-End Tests for Authentication Flow
 * 
 * Complete user journey: Registration → Login → Profile Access → Logout
 * 
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend dev server running on http://localhost:5173
 * - Clean database state
 */

import { test, expect, Page } from '@playwright/test'

// Helper function to generate unique email
function generateEmail() {
  return `testuser${Date.now()}@example.com`
}

// Helper to wait for navigation
async function waitForNavigation(page: Page, expectedPath: string) {
  await page.waitForURL(`**${expectedPath}`, { timeout: 5000 })
}

test.describe('Authentication Flow E2E', () => {
  let testEmail: string
  const testPassword = 'TestPassword123!'
  const testName = 'E2E Test User'

  test.beforeEach(async ({ page }) => {
    // Generate unique email for this test run
    testEmail = generateEmail()
    
    // Navigate to home page
    await page.goto('/')
  })

  test('complete authentication journey: register → login → profile → logout', async ({ page }) => {
    // Step 1: Navigate to registration page
    await page.click('a[href*="register"]')
    await waitForNavigation(page, '/register')
    
    // Step 2: Fill registration form
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    await page.fill('input[name="full_name"]', testName)
    
    // Step 3: Submit registration
    await page.click('button[type="submit"]')
    
    // Step 4: Should be redirected to profile or home after successful registration
    await page.waitForURL(/\/(profile|$)/, { timeout: 5000 })
    
    // Step 5: Verify user is logged in (should see profile or logout button)
    const isLoggedIn = await page.locator('text=/logout|profile/i').isVisible()
    expect(isLoggedIn).toBe(true)
    
    // Step 6: Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")')
    await page.waitForTimeout(500)
    
    // Step 7: Should be redirected to home or login
    await page.waitForURL(/\/(login|$)/, { timeout: 5000 })
    
    // Step 8: Login with same credentials
    // If not already on login page, navigate there
    const currentUrl = page.url()
    if (!currentUrl.includes('/login')) {
      await page.click('a[href*="login"]')
      await waitForNavigation(page, '/login')
    }
    
    // Step 9: Fill login form
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    // Step 10: Submit login
    await page.click('button[type="submit"]')
    
    // Step 11: Should be redirected to profile
    await page.waitForURL(/\/(profile|$)/, { timeout: 5000 })
    
    // Step 12: Verify profile page content
    await expect(page.locator(`text=${testEmail}`)).toBeVisible()
    
    // Step 13: Logout again
    await page.click('button:has-text("Logout"), a:has-text("Logout")')
    await page.waitForTimeout(500)
    
    // Step 14: Verify logged out
    await page.waitForURL(/\/(login|$)/, { timeout: 5000 })
  })

  test('user registration with valid data', async ({ page }) => {
    // Navigate to registration
    await page.goto('/register')
    
    // Fill form
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    const nameInput = page.locator('input[name="full_name"]')
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    // Submit
    await page.click('button[type="submit"]')
    
    // Wait for redirect
    await page.waitForURL(/\/(profile|$)/, { timeout: 5000 })
    
    // Verify success
    expect(page.url()).toMatch(/\/(profile|$)/)
  })

  test('registration fails with duplicate email', async ({ page }) => {
    // First registration
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    const nameInput = page.locator('input[name="full_name"]')
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    await page.click('button[type="submit"]')
    await page.waitForTimeout(1000)
    
    // Logout
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout")')
    if (await logoutButton.isVisible()) {
      await logoutButton.click()
      await page.waitForTimeout(500)
    }
    
    // Try to register again with same email
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    await page.click('button[type="submit"]')
    
    // Should see error message
    await expect(page.locator('text=/already|exists|registered/i')).toBeVisible({ timeout: 3000 })
  })

  test('login with valid credentials', async ({ page }) => {
    // First, register a user
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    const nameInput = page.locator('input[name="full_name"]')
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    await page.click('button[type="submit"]')
    await page.waitForTimeout(1000)
    
    // Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")')
    await page.waitForTimeout(500)
    
    // Now login
    await page.goto('/login')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    await page.click('button[type="submit"]')
    
    // Should redirect to profile
    await page.waitForURL(/\/(profile|$)/, { timeout: 5000 })
    expect(page.url()).toMatch(/\/(profile|$)/)
  })

  test('login fails with invalid credentials', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('input[type="email"]', 'nonexistent@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    
    // Should show error message
    await expect(page.locator('text=/invalid|incorrect|failed/i')).toBeVisible({ timeout: 3000 })
    
    // Should remain on login page
    expect(page.url()).toContain('/login')
  })

  test('profile page access requires authentication', async ({ page }) => {
    // Try to access profile without logging in
    await page.goto('/profile')
    
    // Should redirect to login
    await page.waitForURL('**/login**', { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })

  test('profile page shows user information', async ({ page }) => {
    // Register and login
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    const nameInput = page.locator('input[name="full_name"]')
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    await page.click('button[type="submit"]')
    
    // Navigate to profile
    await page.goto('/profile')
    
    // Verify user info is displayed
    await expect(page.locator(`text=${testEmail}`)).toBeVisible()
    
    if (testName) {
      await expect(page.locator(`text=${testName}`)).toBeVisible()
    }
  })

  test('user can update profile information', async ({ page }) => {
    // Register user
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    
    const nameInput = page.locator('input[name="full_name"]')
    if (await nameInput.isVisible()) {
      await nameInput.fill(testName)
    }
    
    await page.click('button[type="submit"]')
    
    // Navigate to profile
    await page.goto('/profile')
    
    // Look for edit button or form
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Update")')
    
    if (await editButton.isVisible()) {
      await editButton.click()
      
      // Update name
      const profileNameInput = page.locator('input[name="full_name"]').last()
      await profileNameInput.clear()
      await profileNameInput.fill('Updated Name')
      
      // Save changes
      await page.click('button:has-text("Save"), button:has-text("Update")')
      
      // Verify update
      await expect(page.locator('text=Updated Name')).toBeVisible({ timeout: 3000 })
    }
  })

  test('logout clears authentication state', async ({ page }) => {
    // Register and login
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', testPassword)
    await page.click('button[type="submit"]')
    await page.waitForTimeout(1000)
    
    // Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")')
    await page.waitForTimeout(500)
    
    // Try to access profile
    await page.goto('/profile')
    
    // Should redirect to login
    await page.waitForURL('**/login**', { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })

  test('password visibility toggle works', async ({ page }) => {
    await page.goto('/login')
    
    const passwordInput = page.locator('input[type="password"]')
    
    // Check if there's a password visibility toggle
    const toggleButton = page.locator('button:has-text("Show"), button[aria-label*="password"]')
    
    if (await toggleButton.isVisible()) {
      await passwordInput.fill('mypassword')
      
      // Click toggle
      await toggleButton.click()
      
      // Password should now be visible (type="text")
      const visibleInput = page.locator('input[type="text"]')
      expect(await visibleInput.inputValue()).toBe('mypassword')
    }
  })

  test('form validation prevents empty submission', async ({ page }) => {
    await page.goto('/login')
    
    // Try to submit empty form
    await page.click('button[type="submit"]')
    
    // Should show validation errors or prevent submission
    // The form should still be on login page
    expect(page.url()).toContain('/login')
  })
})

test.describe('Navigation and Redirects', () => {
  test('authenticated user redirected from login page', async ({ page }) => {
    const testEmail = generateEmail()
    
    // Register user
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForTimeout(1000)
    
    // Try to access login page while authenticated
    await page.goto('/login')
    
    // Should redirect away from login (to profile or home)
    await page.waitForTimeout(500)
    expect(page.url()).not.toContain('/login')
  })

  test('redirect to intended page after login', async ({ page }) => {
    const testEmail = generateEmail()
    
    // Register user
    await page.goto('/register')
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForTimeout(1000)
    
    // Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")')
    await page.waitForTimeout(500)
    
    // Try to access protected page
    await page.goto('/profile')
    
    // Should redirect to login
    await page.waitForURL('**/login**', { timeout: 5000 })
    
    // Login
    await page.fill('input[type="email"]', testEmail)
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    
    // Should redirect back to profile
    await page.waitForURL('**/profile**', { timeout: 5000 })
    expect(page.url()).toContain('/profile')
  })
})

