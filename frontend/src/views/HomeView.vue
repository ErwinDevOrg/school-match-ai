<template>
  <div class="home">
    <h1>Welcome to School Match AI</h1>
    <p>FastAPI + Vue 3 Starter Application</p>
    
    <div class="links">
      <router-link to="/login" class="btn">Login</router-link>
      <router-link to="/register" class="btn">Register</router-link>
    </div>
    
    <div class="api-info">
      <h3>Quick Links</h3>
      <a href="http://localhost:8000/docs" target="_blank">API Docs</a>
      <a href="http://localhost:8000/health" target="_blank">Health Check</a>
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple home view
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #1a202c;
}

p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}

.links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 0.375rem;
  font-weight: 500;
}

.btn:hover {
  background-color: #2563eb;
  text-decoration: none;
}

.api-info {
  margin-top: 3rem;
  padding: 2rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
}

.api-info h3 {
  margin-bottom: 1rem;
  color: #374151;
}

.api-info a {
  display: block;
  margin: 0.5rem 0;
  color: #3b82f6;
}
</style>
