import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import type { AppError } from '@/lib/errors/AppError'
import { ErrorSeverity } from '@/lib/errors/AppError'
import { parseError } from '@/lib/errors/errorParser'
import { errorLogger } from '@/lib/errors/errorLogger'

export function useErrorHandler() {
  const { t } = useI18n()
  const router = useRouter()
  const { showToast } = useToast()

  async function handleError(
    error: unknown,
    options: {
      showNotification?: boolean
      logError?: boolean
      context?: string
    } = {},
  ): Promise<AppError> {
    const { showNotification = true, logError = true, context } = options

    const appError = await parseError(error, context)

    if (logError) {
      errorLogger.logError(appError, { context })
    }

    if (showNotification) {
      showErrorNotification(appError)
    }

    handleErrorAction(appError)

    return appError
  }

  function showErrorNotification(error: AppError) {
    const message = error.userMessage.startsWith('errors.')
      ? t(error.userMessage)
      : error.userMessage

    const variant = getToastVariant(error.severity)

    showToast({
      title: t(`errors.${error.category.toLowerCase()}.title`),
      description: message,
      variant,
      duration: error.severity === ErrorSeverity.CRITICAL ? 10000 : 5000,
    })
  }

  function getToastVariant(severity: ErrorSeverity): 'error' | 'warning' {
    return severity === ErrorSeverity.CRITICAL || severity === ErrorSeverity.HIGH
      ? 'error'
      : 'warning'
  }

  function handleErrorAction(error: AppError) {
    if (error.action === 'LOGIN') {
      router.push({ name: 'login' })
    }
  }

  function handleAuthError(error: unknown) {
    return handleError(error, {
      showNotification: true,
      logError: true,
      context: 'Authentication',
    })
  }

  function handleApiError(error: unknown, context?: string) {
    return handleError(error, {
      showNotification: true,
      logError: true,
      context: context || 'API Call',
    })
  }

  return {
    handleError,
    handleAuthError,
    handleApiError,
  }
}
