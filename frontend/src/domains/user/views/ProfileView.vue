<template>
  <div class="profile-view">
    <div class="profile-container">
      <div class="profile-header">
        <h1 class="title">My Profile</h1>
        <BaseButton @click="handleLogout" variant="secondary">
          Logout
        </BaseButton>
      </div>
      
      <div v-if="loading" class="loading">Loading...</div>
      
      <div v-else-if="user" class="profile-content">
        <form @submit.prevent="handleUpdateProfile" class="profile-form">
          <BaseInput
            v-model="formData.email"
            type="email"
            label="Email"
            :error="errors.email"
          />
          
          <BaseInput
            v-model="formData.full_name"
            type="text"
            label="Full Name"
          />
          
          <div class="profile-info">
            <p><strong>Account Status:</strong> {{ user.is_active ? 'Active' : 'Inactive' }}</p>
            <p><strong>Verified:</strong> {{ user.is_verified ? 'Yes' : 'No' }}</p>
            <p><strong>Member Since:</strong> {{ formatDate(user.created_at) }}</p>
          </div>
          
          <div v-if="errors.general" class="error-box">
            {{ errors.general }}
          </div>
          
          <div v-if="successMessage" class="success-box">
            {{ successMessage }}
          </div>
          
          <BaseButton
            type="submit"
            :loading="updating"
            full-width
          >
            Update Profile
          </BaseButton>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/domains/auth/composables/useAuth'
import { useUser } from '../composables/useUser'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseButton from '@/shared/components/BaseButton.vue'

const router = useRouter()
const { user, logout } = useAuth()
const { updateProfile } = useUser()

const loading = ref(true)
const updating = ref(false)
const errors = ref<Record<string, string>>({})
const successMessage = ref('')

const formData = ref({
  email: '',
  full_name: ''
})

onMounted(() => {
  if (user.value) {
    formData.value.email = user.value.email
    formData.value.full_name = user.value.full_name || ''
  }
  loading.value = false
})

watch(user, (newUser) => {
  if (newUser) {
    formData.value.email = newUser.email
    formData.value.full_name = newUser.full_name || ''
  }
})

async function handleUpdateProfile() {
  updating.value = true
  errors.value = {}
  successMessage.value = ''
  
  try {
    await updateProfile({
      email: formData.value.email,
      full_name: formData.value.full_name || undefined
    })
    
    successMessage.value = 'Profile updated successfully!'
  } catch (error: any) {
    errors.value.general = error.response?.data?.message || 'Failed to update profile.'
  } finally {
    updating.value = false
  }
}

async function handleLogout() {
  await logout()
  router.push('/login')
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background-color: #f3f4f6;
  padding: 2rem 1rem;
}

.profile-container {
  max-width: 42rem;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-info {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.profile-info p {
  font-size: 0.875rem;
  color: #374151;
}

.error-box {
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #991b1b;
  font-size: 0.875rem;
}

.success-box {
  padding: 0.75rem;
  background-color: #d1fae5;
  border: 1px solid #a7f3d0;
  border-radius: 0.375rem;
  color: #065f46;
  font-size: 0.875rem;
}
</style>

