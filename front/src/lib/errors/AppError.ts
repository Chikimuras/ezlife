export const ErrorCategory = {
  NETWORK: 'NETWORK',
  AUTH: 'AUTH',
  VALIDATION: 'VALIDATION',
  NOT_FOUND: 'NOT_FOUND',
  PERMISSION: 'PERMISSION',
  SERVER: 'SERVER',
  CLIENT: 'CLIENT',
  UNKNOWN: 'UNKNOWN',
} as const

export type ErrorCategory = (typeof ErrorCategory)[keyof typeof ErrorCategory]

export const ErrorSeverity = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
} as const

export type ErrorSeverity = (typeof ErrorSeverity)[keyof typeof ErrorSeverity]

export interface ErrorDetails {
  code: string
  category: ErrorCategory
  severity: ErrorSeverity
  message: string
  userMessage: string
  statusCode?: number
  field?: string
  retry?: boolean
  action?: 'RETRY' | 'LOGIN' | 'CONTACT_SUPPORT' | 'DISMISS'
  metadata?: Record<string, unknown>
}

export class AppError extends Error {
  public readonly code: string
  public readonly category: ErrorCategory
  public readonly severity: ErrorSeverity
  public readonly userMessage: string
  public readonly statusCode?: number
  public readonly field?: string
  public readonly retry: boolean
  public readonly action?: 'RETRY' | 'LOGIN' | 'CONTACT_SUPPORT' | 'DISMISS'
  public readonly metadata?: Record<string, unknown>
  public readonly timestamp: Date

  constructor(details: ErrorDetails) {
    super(details.message)
    this.name = 'AppError'
    this.code = details.code
    this.category = details.category
    this.severity = details.severity
    this.userMessage = details.userMessage
    this.statusCode = details.statusCode
    this.field = details.field
    this.retry = details.retry ?? false
    this.action = details.action
    this.metadata = details.metadata
    this.timestamp = new Date()

    Object.setPrototypeOf(this, AppError.prototype)
  }

  toJSON() {
    return {
      name: this.name,
      code: this.code,
      category: this.category,
      severity: this.severity,
      message: this.message,
      userMessage: this.userMessage,
      statusCode: this.statusCode,
      field: this.field,
      retry: this.retry,
      action: this.action,
      metadata: this.metadata,
      timestamp: this.timestamp.toISOString(),
      stack: import.meta.env.DEV ? this.stack : undefined,
    }
  }
}

export class NetworkError extends AppError {
  constructor(message: string, userMessage: string, metadata?: Record<string, unknown>) {
    super({
      code: 'NETWORK_ERROR',
      category: ErrorCategory.NETWORK,
      severity: ErrorSeverity.HIGH,
      message,
      userMessage,
      retry: true,
      action: 'RETRY',
      metadata,
    })
  }
}

export class AuthError extends AppError {
  constructor(message: string, userMessage: string, statusCode?: number) {
    super({
      code: 'AUTH_ERROR',
      category: ErrorCategory.AUTH,
      severity: ErrorSeverity.HIGH,
      message,
      userMessage,
      statusCode,
      retry: false,
      action: 'LOGIN',
    })
  }
}

export class ValidationError extends AppError {
  constructor(
    message: string,
    userMessage: string,
    field?: string,
    metadata?: Record<string, unknown>,
  ) {
    super({
      code: 'VALIDATION_ERROR',
      category: ErrorCategory.VALIDATION,
      severity: ErrorSeverity.LOW,
      message,
      userMessage,
      field,
      retry: false,
      action: 'DISMISS',
      metadata,
    })
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, userMessage: string) {
    super({
      code: 'NOT_FOUND',
      category: ErrorCategory.NOT_FOUND,
      severity: ErrorSeverity.MEDIUM,
      message: `Resource not found: ${resource}`,
      userMessage,
      statusCode: 404,
      retry: false,
      action: 'DISMISS',
    })
  }
}

export class ServerError extends AppError {
  constructor(message: string, userMessage: string, statusCode: number = 500) {
    super({
      code: 'SERVER_ERROR',
      category: ErrorCategory.SERVER,
      severity: ErrorSeverity.CRITICAL,
      message,
      userMessage,
      statusCode,
      retry: true,
      action: 'RETRY',
    })
  }
}
