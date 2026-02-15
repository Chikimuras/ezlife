import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/lib/api/auth'
import type { User } from '@/lib/api/schemas/auth'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))

  // Restore user from localStorage on initialization
  const storedUser = localStorage.getItem('auth_user')
  const user = ref<User | null>(storedUser ? JSON.parse(storedUser) : null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const onTokenUpdatedCallbacks: Array<(token: string) => void> = []

  const { handleAuthError } = useErrorHandler()

  const onTokenUpdated = (callback: (token: string) => void) => {
    onTokenUpdatedCallbacks.push(callback)
  }

  const notifyTokenUpdated = (newToken: string) => {
    onTokenUpdatedCallbacks.forEach((callback) => callback(newToken))
  }

  const setAuth = (accessToken: string, userData: User) => {
    token.value = accessToken
    user.value = userData
    localStorage.setItem('auth_token', accessToken)
    localStorage.setItem('auth_user', JSON.stringify(userData))
    error.value = null
    notifyTokenUpdated(accessToken)
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  const loginWithGoogle = async (googleToken: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await authApi.loginWithGoogle(googleToken)
      setAuth(response.accessToken, response.user)
      errorLogger.logInfo('User logged in successfully via Google', { userId: response.user.id })
      return response
    } catch (err) {
      error.value = 'Google login failed'
      await handleAuthError(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchCurrentUser = async (): Promise<boolean> => {
    if (!token.value) {
      return false
    }

    try {
      isLoading.value = true
      error.value = null
      const response = await authApi.me()
      user.value = response.user
      localStorage.setItem('auth_user', JSON.stringify(response.user))
      return true
    } catch (err) {
      error.value = 'Failed to fetch user'
      errorLogger.logError(err, { context: 'Fetch Current User' })
      clearAuth()
      return false
    } finally {
      isLoading.value = false
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      error.value = null
      const response = await authApi.refresh()
      if (token.value) {
        localStorage.setItem('auth_token', response.accessToken)
        token.value = response.accessToken
        notifyTokenUpdated(response.accessToken)
      }
      errorLogger.logInfo('Token refreshed successfully')
      return true
    } catch (err) {
      error.value = 'Token refresh failed'
      errorLogger.logError(err, { context: 'Token Refresh', severity: 'HIGH' })
      clearAuth()
      return false
    }
  }

  const logout = async () => {
    try {
      error.value = null
      await authApi.logout()
      errorLogger.logInfo('User logged out successfully')
    } catch (err) {
      error.value = 'Logout failed'
      errorLogger.logWarning('Logout API call failed', { error: err })
    } finally {
      clearAuth()
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    error,
    loginWithGoogle,
    fetchCurrentUser,
    refreshToken,
    logout,
    onTokenUpdated,
  }
})
