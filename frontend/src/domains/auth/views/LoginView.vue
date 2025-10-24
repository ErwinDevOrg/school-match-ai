<template>
  <div class="login-view">
    <div class="login-card">
      <h1 class="title">Login</h1>
      <p class="subtitle">Welcome back! Please login to your account.</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <BaseInput
          v-model="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          required
          :error="errors.email"
        />
        
        <BaseInput
          v-model="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
          :error="errors.password"
        />
        
        <div v-if="errors.general" class="error-box">
          {{ errors.general }}
        </div>
        
        <BaseButton
          type="submit"
          :loading="loading"
          full-width
        >
          Login
        </BaseButton>
      </form>
      
      <p class="footer-text">
        Don't have an account?
        <router-link to="/register" class="link">Register here</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseButton from '@/shared/components/BaseButton.vue'

const router = useRouter()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errors = ref<Record<string, string>>({})

async function handleLogin() {
  loading.value = true
  errors.value = {}
  
  try {
    await login({
      email: email.value,
      password: password.value
    })
    
    // Redirect to profile after successful login
    router.push('/profile')
  } catch (error: any) {
    errors.value.general = error.response?.data?.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 28rem;
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.error-box {
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #991b1b;
  font-size: 0.875rem;
}

.footer-text {
  margin-top: 1.5rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}
</style>

