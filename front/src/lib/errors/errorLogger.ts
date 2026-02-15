import type { AppError } from './AppError'

interface ErrorLoggerConfig {
  enabled: boolean
  dsn?: string
  environment?: string
  release?: string
}

class ErrorLogger {
  private config: ErrorLoggerConfig = {
    enabled: import.meta.env.PROD,
    environment: import.meta.env.MODE,
  }

  private sentryInitialized = false

  configure(config: Partial<ErrorLoggerConfig>) {
    this.config = { ...this.config, ...config }
  }

  async initSentry() {
    if (this.sentryInitialized || !this.config.dsn) {
      return
    }

    try {
      // @ts-ignore - Optional dependency
      const Sentry = await import('@sentry/vue').catch(() => null)
      if (!Sentry) {
        console.warn('Sentry package not installed. Error monitoring disabled.')
        return
      }

      Sentry.init({
        dsn: this.config.dsn,
        environment: this.config.environment,
        release: this.config.release,
        integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
        tracesSampleRate: 0.1,
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
      })
      this.sentryInitialized = true
    } catch (error) {
      console.error('Failed to initialize Sentry:', error)
    }
  }

  logError(error: unknown, context?: Record<string, unknown>) {
    if (!this.config.enabled) {
      this.logToConsole(error, context)
      return
    }

    this.logToConsole(error, context)

    if (this.sentryInitialized) {
      this.logToSentry(error, context)
    }
  }

  private logToConsole(error: unknown, context?: Record<string, unknown>) {
    if (import.meta.env.DEV) {
      const message = error instanceof Error ? error.message : String(error)
      console.group(`🔴 Error: ${message}`)
      console.error(error)
      if (context) {
        console.log('Context:', context)
      }
      console.groupEnd()
    }
  }

  private async logToSentry(error: unknown, context?: Record<string, unknown>) {
    try {
      // @ts-ignore - Optional dependency
      const Sentry = await import('@sentry/vue').catch(() => null)
      if (!Sentry) return

      if (error instanceof Error) {
        Sentry.captureException(error, {
          extra: {
            ...(context || {}),
            ...(error as AppError).metadata,
          },
          tags: {
            category: (error as AppError).category,
            severity: (error as AppError).severity,
            code: (error as AppError).code,
          },
          level:
            (error as AppError).severity === 'CRITICAL'
              ? 'fatal'
              : (error as AppError).severity === 'HIGH'
                ? 'error'
                : (error as AppError).severity === 'MEDIUM'
                  ? 'warning'
                  : 'info',
        })
      }
    } catch (err) {
      console.error('Failed to log to Sentry:', err)
    }
  }

  logInfo(message: string, context?: Record<string, unknown>) {
    if (import.meta.env.DEV) {
      console.log(`ℹ️ ${message}`, context)
    }
  }

  logWarning(message: string, context?: Record<string, unknown>) {
    if (import.meta.env.DEV) {
      console.warn(`⚠️ ${message}`, context)
    }
  }
}

export const errorLogger = new ErrorLogger()
