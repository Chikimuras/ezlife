import { HTTPError, TimeoutError } from 'ky'
import { ZodError } from 'zod'
import {
  AppError,
  NetworkError,
  AuthError,
  ValidationError,
  NotFoundError,
  ServerError,
  ErrorCategory,
  ErrorSeverity,
} from './AppError'

interface BackendErrorResponse {
  code?: string
  message?: string
  detail?: string
  field?: string
  errors?: Array<{ field: string; message: string }>
}

export async function parseError(error: unknown, context?: string): Promise<AppError> {
  if (error instanceof AppError) {
    return error
  }

  if (error instanceof TimeoutError) {
    return new NetworkError('Request timeout', 'errors.network.timeout')
  }

  if (error instanceof HTTPError) {
    return await parseHTTPError(error, context)
  }

  if (error instanceof ZodError) {
    return parseZodError(error, context)
  }

  if (error instanceof Error) {
    if ((error as any).zodError instanceof ZodError) {
      const zodError = (error as any).zodError as ZodError
      const responseContext = (error as any).context || context
      return parseZodError(zodError, responseContext)
    }
  }

  if (!navigator.onLine) {
    return new NetworkError('No internet connection', 'errors.network.offline')
  }

  if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
    return new NetworkError('Network request failed', 'errors.network.generic')
  }

  return new AppError({
    code: 'UNKNOWN_ERROR',
    category: ErrorCategory.UNKNOWN,
    severity: ErrorSeverity.MEDIUM,
    message: error instanceof Error ? error.message : 'Unknown error',
    userMessage: 'errors.unknown.generic',
    retry: false,
    action: 'DISMISS',
  })
}

async function parseHTTPError(error: HTTPError, context?: string): Promise<AppError> {
  const statusCode = error.response.status

  let backendError: BackendErrorResponse | null = null
  try {
    backendError = await error.response.json()
  } catch {
    backendError = null
  }

  const message = backendError?.message || backendError?.detail || error.message
  const code = backendError?.code || `HTTP_${statusCode}`

  switch (statusCode) {
    case 400:
      if (backendError?.errors && Array.isArray(backendError.errors)) {
        const firstError = backendError.errors[0]
        return new ValidationError(
          message,
          firstError?.message || 'errors.validation.generic',
          firstError?.field,
        )
      }
      return new ValidationError(message, 'errors.validation.generic', backendError?.field)

    case 401:
      return new AuthError(message, 'errors.auth.sessionExpired', statusCode)

    case 403:
      return new AuthError(message, 'errors.auth.unauthorized', statusCode)

    case 404:
      return new NotFoundError(context || 'Resource', 'errors.notFound.resource')

    case 409:
      return new ValidationError(message, message, backendError?.field)

    case 422:
      return new ValidationError(message, 'errors.validation.generic', backendError?.field)

    case 429:
      return new AppError({
        code: 'RATE_LIMIT',
        category: ErrorCategory.CLIENT,
        severity: ErrorSeverity.MEDIUM,
        message: 'Too many requests',
        userMessage: 'Too many requests. Please wait a moment and try again.',
        statusCode,
        retry: true,
        action: 'RETRY',
      })

    case 500:
    case 502:
    case 503:
    case 504:
      return new ServerError(message, 'errors.server.internal', statusCode)

    default:
      if (statusCode >= 500) {
        return new ServerError(message, 'errors.server.generic', statusCode)
      }
      return new AppError({
        code,
        category: ErrorCategory.CLIENT,
        severity: ErrorSeverity.MEDIUM,
        message,
        userMessage: message,
        statusCode,
        retry: false,
        action: 'DISMISS',
      })
  }
}

function parseZodError(error: ZodError, context?: string): ValidationError {
  const firstError = error.issues[0]
  const field = firstError?.path.join('.') || 'unknown'

  let userMessage = 'errors.validation.generic'
  let detailedMessage = firstError?.message || 'Validation error'

  if (context === 'API Response Validation') {
    userMessage = 'errors.server.generic'
    detailedMessage = `Server returned invalid data: ${field} - ${firstError?.message}`
  } else if (firstError?.code === 'invalid_type') {
    const issue = firstError as { expected?: string; received?: unknown }
    if (issue.expected === 'string' && issue.received === 'undefined') {
      detailedMessage = `Missing required field: ${field}`
    }
  }

  return new ValidationError(detailedMessage, userMessage, field, {
    zodErrors: error.issues,
  })
}
