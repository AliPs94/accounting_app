import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authAPI } from '@/services/apiService'
import type { User } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userFullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })

  // Actions
  const setTokens = (accessToken: string, refresh: string) => {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refresh)
  }

  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    error.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const login = async (credentials: { username: string; password: string }) => {
    isLoading.value = true
    error.value = null
    
    try {
      console.log('Attempting login with:', credentials.username)
      const response = await authAPI.login(credentials)
      console.log('Login response:', response)
      
      if (response.data.tokens && response.data.tokens.access && response.data.user) {
        setTokens(response.data.tokens.access, response.data.tokens.refresh)
        setUser(response.data.user)
        return { success: true }
      } else {
        return { success: false, error: 'Invalid response from server' }
      }
    } catch (err: any) {
      console.error('Login error:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error || 'Login failed'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.register(userData)
      if (response.data.tokens && response.data.tokens.access && response.data.user) {
        setTokens(response.data.tokens.access, response.data.tokens.refresh)
        setUser(response.data.user)
        return { success: true }
      } else {
        return { success: false, error: 'Registration failed' }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.error || 'Registration failed'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    clearAuth()
  }

  const loadUserFromStorage = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefresh = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')
    
    console.log('Loading user from storage:', { storedToken: !!storedToken, storedRefresh: !!storedRefresh, storedUser: !!storedUser })
    
    if (storedToken && storedRefresh && storedUser) {
      token.value = storedToken
      refreshToken.value = storedRefresh
      try {
        user.value = JSON.parse(storedUser)
        console.log('User loaded from storage:', user.value)
      } catch (e) {
        console.error('Failed to parse stored user data')
        clearAuth()
      }
    } else {
      console.log('No stored auth data found')
    }
  }

  const refreshUserToken = async () => {
    if (!refreshToken.value) return false
    
    try {
      const response = await authAPI.refreshToken(refreshToken.value)
      if (response.data.access) {
        token.value = response.data.access
        localStorage.setItem('access_token', response.data.access)
        return true
      }
    } catch (err) {
      console.error('Token refresh failed:', err)
      clearAuth()
    }
    return false
  }

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    userFullName,
    // Actions
    setTokens,
    setUser,
    clearAuth,
    login,
    register,
    logout,
    loadUserFromStorage,
    refreshUserToken
  }
})