import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/lib/api/auth'
import type { User } from '@/lib/api/schemas/auth'
import { startAuthentication, startRegistration } from '@simplewebauthn/browser'

const handleAuthErrorMock = vi.fn(async () => undefined)
const handleApiErrorMock = vi.fn(async () => undefined)
const routerPushMock = vi.fn()

vi.mock('@/lib/api/auth', () => ({
  authApi: {
    getLoginOptions: vi.fn(),
    verifyLogin: vi.fn(),
    getRegisterOptions: vi.fn(),
    verifyRegistration: vi.fn(),
    me: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  },
}))

vi.mock('@simplewebauthn/browser', () => ({
  startAuthentication: vi.fn(),
  startRegistration: vi.fn(),
}))

vi.mock('@/composables/useErrorHandler', () => ({
  useErrorHandler: () => ({
    handleAuthError: handleAuthErrorMock,
    handleApiError: handleApiErrorMock,
  }),
}))

vi.mock('@/lib/errors/errorLogger', () => ({
  errorLogger: {
    logInfo: vi.fn(),
    logError: vi.fn(),
    logWarning: vi.fn(),
  },
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPushMock,
  }),
}))

const baseUser: User = {
  id: '11111111-1111-4111-8111-111111111111',
  email: 'a@b.com',
  name: 'Test',
  createdAt: '2024-01-01',
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })
  })

  it('loginWithPasskey success sets auth state and persists data', async () => {
    const store = useAuthStore()
    const options = { challenge: 'opts' }
    const credential = { id: 'cred', rawId: 'cred', response: {} }
    const response = { accessToken: 'tok', user: baseUser }
    vi.mocked(authApi.getLoginOptions).mockResolvedValue(options)
    vi.mocked(startAuthentication).mockResolvedValue(
      credential as Awaited<ReturnType<typeof startAuthentication>>,
    )
    vi.mocked(authApi.verifyLogin).mockResolvedValue(response)

    const result = await store.loginWithPasskey()

    expect(result).toEqual(response)
    expect(authApi.getLoginOptions).toHaveBeenCalledOnce()
    expect(startAuthentication).toHaveBeenCalledWith({ optionsJSON: options })
    expect(authApi.verifyLogin).toHaveBeenCalledWith(credential)
    expect(store.token).toBe('tok')
    expect(store.user).toEqual(baseUser)
    expect(store.isAuthenticated).toBe(true)
    expect(store.isLoading).toBe(false)
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'tok')
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(baseUser))
  })

  it('loginWithPasskey failure sets error and delegates handling', async () => {
    const store = useAuthStore()
    const failure = new Error('user cancelled')
    vi.mocked(authApi.getLoginOptions).mockResolvedValue({ challenge: 'opts' })
    vi.mocked(startAuthentication).mockRejectedValue(failure)

    await expect(store.loginWithPasskey()).rejects.toThrow('user cancelled')

    expect(store.error).toBe('Passkey login failed')
    expect(store.isLoading).toBe(false)
    expect(handleAuthErrorMock).toHaveBeenCalledWith(failure)
  })

  it('registerWithPasskey success sets auth state', async () => {
    const store = useAuthStore()
    const options = { challenge: 'opts' }
    const credential = { id: 'cred', rawId: 'cred', response: {} }
    const response = { accessToken: 'new-tok', user: baseUser }
    vi.mocked(authApi.getRegisterOptions).mockResolvedValue(options)
    vi.mocked(startRegistration).mockResolvedValue(
      credential as Awaited<ReturnType<typeof startRegistration>>,
    )
    vi.mocked(authApi.verifyRegistration).mockResolvedValue(response)

    const result = await store.registerWithPasskey({
      email: 'new@example.com',
      name: 'New',
    })

    expect(result).toEqual(response)
    expect(authApi.getRegisterOptions).toHaveBeenCalledWith('new@example.com', 'New')
    expect(startRegistration).toHaveBeenCalledWith({ optionsJSON: options })
    expect(authApi.verifyRegistration).toHaveBeenCalledWith(credential)
    expect(store.token).toBe('new-tok')
    expect(store.user).toEqual(baseUser)
    expect(store.isAuthenticated).toBe(true)
  })

  it('registerWithPasskey failure sets error and delegates handling', async () => {
    const store = useAuthStore()
    const failure = new Error('attestation failed')
    vi.mocked(authApi.getRegisterOptions).mockResolvedValue({ challenge: 'opts' })
    vi.mocked(startRegistration).mockRejectedValue(failure)

    await expect(
      store.registerWithPasskey({ email: 'new@example.com', name: 'New' }),
    ).rejects.toThrow('attestation failed')

    expect(store.error).toBe('Passkey registration failed')
    expect(store.isLoading).toBe(false)
    expect(handleAuthErrorMock).toHaveBeenCalledWith(failure)
  })

  it('fetchCurrentUser success updates user and keeps auth', async () => {
    const store = useAuthStore()
    store.token = 'tok'
    const updatedUser: User = { ...baseUser, name: 'Updated' }
    vi.mocked(authApi.me).mockResolvedValue({ user: updatedUser })

    const result = await store.fetchCurrentUser()

    expect(result).toBe(true)
    expect(store.user).toEqual(updatedUser)
    expect(store.error).toBe(null)
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(updatedUser))
  })

  it('fetchCurrentUser without token returns false and skips API call', async () => {
    const store = useAuthStore()

    const result = await store.fetchCurrentUser()

    expect(result).toBe(false)
    expect(vi.mocked(authApi.me)).not.toHaveBeenCalled()
  })

  it('fetchCurrentUser failure clears auth and returns false', async () => {
    const store = useAuthStore()
    store.token = 'tok'
    store.user = baseUser
    vi.mocked(authApi.me).mockRejectedValue(new Error('me failed'))

    const result = await store.fetchCurrentUser()

    expect(result).toBe(false)
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.error).toBe('Failed to fetch user')
    expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
    expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
  })

  it('refreshToken success updates token when authenticated', async () => {
    const store = useAuthStore()
    store.token = 'tok-old'
    store.user = baseUser
    vi.mocked(authApi.refresh).mockResolvedValue({ accessToken: 'tok-new' })

    const result = await store.refreshToken()

    expect(result).toBe(true)
    expect(store.token).toBe('tok-new')
    expect(store.error).toBe(null)
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'tok-new')
  })

  it('refreshToken failure clears auth and returns false', async () => {
    const store = useAuthStore()
    store.token = 'tok-old'
    store.user = baseUser
    vi.mocked(authApi.refresh).mockRejectedValue(new Error('refresh failed'))

    const result = await store.refreshToken()

    expect(result).toBe(false)
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.error).toBe('Token refresh failed')
  })

  it('logout clears auth state', async () => {
    const store = useAuthStore()
    store.token = 'tok'
    store.user = baseUser
    vi.mocked(authApi.logout).mockResolvedValue(undefined)

    await store.logout()

    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
    expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
  })

  it('isAuthenticated is true only when token and user exist', () => {
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(false)

    store.token = 'tok'
    expect(store.isAuthenticated).toBe(false)

    store.user = baseUser
    expect(store.isAuthenticated).toBe(true)

    store.token = null
    expect(store.isAuthenticated).toBe(false)
  })
})
