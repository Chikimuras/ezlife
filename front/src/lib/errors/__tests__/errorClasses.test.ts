import { describe, expect, it } from 'vitest'
import {
  AppError,
  AuthError,
  ErrorCategory,
  ErrorSeverity,
  NetworkError,
  NotFoundError,
  ServerError,
  ValidationError,
} from '@/lib/errors/AppError'

describe('AppError classes', () => {
  it('AppError construction with all fields', () => {
    const metadata = { requestId: 'req-1', details: { source: 'unit-test' } }
    const error = new AppError({
      code: 'CUSTOM_ERROR',
      category: ErrorCategory.CLIENT,
      severity: ErrorSeverity.MEDIUM,
      message: 'Technical message',
      userMessage: 'Friendly message',
      statusCode: 418,
      field: 'email',
      retry: true,
      action: 'RETRY',
      metadata,
    })

    expect(error.name).toBe('AppError')
    expect(error.code).toBe('CUSTOM_ERROR')
    expect(error.category).toBe(ErrorCategory.CLIENT)
    expect(error.severity).toBe(ErrorSeverity.MEDIUM)
    expect(error.message).toBe('Technical message')
    expect(error.userMessage).toBe('Friendly message')
    expect(error.statusCode).toBe(418)
    expect(error.field).toBe('email')
    expect(error.retry).toBe(true)
    expect(error.action).toBe('RETRY')
    expect(error.metadata).toEqual(metadata)
  })

  it('AppError.toJSON() returns correct structure', () => {
    const error = new AppError({
      code: 'JSON_ERROR',
      category: ErrorCategory.UNKNOWN,
      severity: ErrorSeverity.LOW,
      message: 'Serialize me',
      userMessage: 'errors.unknown.generic',
      retry: false,
      action: 'DISMISS',
    })

    const json = error.toJSON()

    expect(json).toMatchObject({
      name: 'AppError',
      code: 'JSON_ERROR',
      category: ErrorCategory.UNKNOWN,
      severity: ErrorSeverity.LOW,
      message: 'Serialize me',
      userMessage: 'errors.unknown.generic',
      retry: false,
      action: 'DISMISS',
    })
    expect(json.timestamp).toBe(error.timestamp.toISOString())
    expect(json.stack).toBe(error.stack)
  })

  it('NetworkError has correct category, severity, retry and action', () => {
    const error = new NetworkError('Network failed', 'errors.network.generic')

    expect(error.category).toBe(ErrorCategory.NETWORK)
    expect(error.severity).toBe(ErrorSeverity.HIGH)
    expect(error.retry).toBe(true)
    expect(error.action).toBe('RETRY')
  })

  it('AuthError has correct category, severity, retry and action', () => {
    const error = new AuthError('Unauthorized', 'errors.auth.unauthorized', 401)

    expect(error.category).toBe(ErrorCategory.AUTH)
    expect(error.severity).toBe(ErrorSeverity.HIGH)
    expect(error.retry).toBe(false)
    expect(error.action).toBe('LOGIN')
  })

  it('ValidationError has correct category and field is set', () => {
    const error = new ValidationError('Invalid email', 'errors.validation.generic', 'email')

    expect(error.category).toBe(ErrorCategory.VALIDATION)
    expect(error.field).toBe('email')
  })

  it('NotFoundError has correct category and statusCode 404', () => {
    const error = new NotFoundError('User', 'errors.notFound.resource')

    expect(error.category).toBe(ErrorCategory.NOT_FOUND)
    expect(error.statusCode).toBe(404)
  })

  it('ServerError has correct category, severity and retry', () => {
    const error = new ServerError('Internal server error', 'errors.server.internal')

    expect(error.category).toBe(ErrorCategory.SERVER)
    expect(error.severity).toBe(ErrorSeverity.CRITICAL)
    expect(error.retry).toBe(true)
  })

  it('AppError instanceof Error is true', () => {
    const error = new AppError({
      code: 'BASE',
      category: ErrorCategory.UNKNOWN,
      severity: ErrorSeverity.MEDIUM,
      message: 'Base message',
      userMessage: 'errors.unknown.generic',
    })

    expect(error instanceof Error).toBe(true)
  })

  it('AppError instanceof AppError is true', () => {
    const error = new AppError({
      code: 'BASE',
      category: ErrorCategory.UNKNOWN,
      severity: ErrorSeverity.MEDIUM,
      message: 'Base message',
      userMessage: 'errors.unknown.generic',
    })

    expect(error instanceof AppError).toBe(true)
  })

  it('NetworkError instanceof AppError is true', () => {
    const error = new NetworkError('Request failed', 'errors.network.generic')

    expect(error instanceof AppError).toBe(true)
  })

  it('AppError timestamp is a Date', () => {
    const error = new AppError({
      code: 'TIME_ERROR',
      category: ErrorCategory.CLIENT,
      severity: ErrorSeverity.LOW,
      message: 'Has time',
      userMessage: 'errors.unknown.generic',
    })

    expect(error.timestamp).toBeInstanceOf(Date)
  })
})
