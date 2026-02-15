import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getTimeUntilExpiration, isTokenExpired } from '@/lib/utils/jwt'
import { errorLogger } from '@/lib/errors/errorLogger'

const REFRESH_BEFORE_EXPIRY_MS = 5 * 60 * 1000

let refreshTimeoutId: ReturnType<typeof setTimeout> | null = null

export const useTokenRefresh = () => {
  const authStore = useAuthStore()
  const isRefreshing = ref(false)

  const clearRefreshTimeout = () => {
    if (refreshTimeoutId) {
      clearTimeout(refreshTimeoutId)
      refreshTimeoutId = null
    }
  }

  const scheduleTokenRefresh = (token: string) => {
    clearRefreshTimeout()

    if (isTokenExpired(token)) {
      errorLogger.logWarning('Token already expired, logging out')
      authStore.logout()
      return
    }

    const timeUntilExpiry = getTimeUntilExpiration(token)
    const refreshIn = Math.max(0, timeUntilExpiry - REFRESH_BEFORE_EXPIRY_MS)

    errorLogger.logInfo('Scheduling token refresh', {
      refreshIn: `${Math.round(refreshIn / 1000)}s`,
      expiresIn: `${Math.round(timeUntilExpiry / 1000)}s`,
    })

    refreshTimeoutId = setTimeout(async () => {
      await refreshToken()
    }, refreshIn)
  }

  const refreshToken = async () => {
    if (isRefreshing.value) {
      errorLogger.logWarning('Token refresh already in progress, skipping')
      return
    }

    if (!authStore.token) {
      errorLogger.logWarning('No token to refresh')
      return
    }

    try {
      isRefreshing.value = true
      errorLogger.logInfo('Refreshing access token')

      const success = await authStore.refreshToken()

      if (!success) {
        errorLogger.logError('Token refresh failed, logging out')
        authStore.logout()
      }
    } catch (error) {
      errorLogger.logError(error, { context: 'Token Refresh' })
      authStore.logout()
    } finally {
      isRefreshing.value = false
    }
  }

  const startTokenRefreshCycle = () => {
    if (!authStore.token) {
      return
    }

    scheduleTokenRefresh(authStore.token)

    authStore.onTokenUpdated((newToken: string) => {
      scheduleTokenRefresh(newToken)
    })
  }

  const stopTokenRefreshCycle = () => {
    clearRefreshTimeout()
  }

  onUnmounted(() => {
    clearRefreshTimeout()
  })

  return {
    isRefreshing,
    startTokenRefreshCycle,
    stopTokenRefreshCycle,
    refreshToken,
  }
}
