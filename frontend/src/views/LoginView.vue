<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>{{ $t('app.title') }}</h1>
        <p>{{ $t('auth.signIn') }}</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">{{ $t('auth.username') }}</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            required
            :disabled="isLoading"
            :placeholder="$t('auth.username')"
          />
        </div>

        <div class="form-group">
          <label for="password">{{ $t('auth.password') }}</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            :disabled="isLoading"
            :placeholder="$t('auth.password')"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="isLoading || !credentials.username || !credentials.password"
          class="login-button"
        >
          <span v-if="isLoading">{{ $t('auth.signingIn') }}</span>
          <span v-else>{{ $t('auth.signIn') }}</span>
        </button>
      </form>

      <div class="login-footer">
        <p>{{ $t('auth.demoCredentials') }}:</p>
        <p><strong>{{ $t('auth.username') }}:</strong> admin</p>
        <p><strong>{{ $t('auth.password') }}:</strong> admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials } from '@/types/auth'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const credentials = reactive<LoginCredentials>({
  username: '',
  password: ''
})

const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!credentials.username || !credentials.password) {
    error.value = t('auth.fillAllFields')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    console.log('Attempting login with:', credentials)
    const result = await authStore.login(credentials)
    console.log('Login result:', result)
    
    if (result.success) {
      // Redirect to dashboard or home page
      router.push('/')
    } else {
      error.value = result.error || t('auth.loginFailed')
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = t('auth.unexpectedError')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.login-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
  border: 1px solid #fcc;
}

.login-button {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e1e5e9;
}

.login-footer p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.login-footer p:first-child {
  font-weight: 500;
  margin-bottom: 8px;
}

.login-footer strong {
  color: #333;
}
</style>

