import { api, fetcher } from './client'
import {
  LoginResponseSchema,
  RefreshResponseSchema,
  MeResponseSchema,
  WebAuthnOptionsSchema,
  PasskeyListResponseSchema,
  PasskeyCreatedResponseSchema,
  type LoginResponse,
  type RefreshResponse,
  type MeResponse,
  type WebAuthnOptions,
  type PasskeyListResponse,
  type PasskeyCreatedResponse,
} from './schemas/auth'

export const authApi = {
  // ------------------------------------------------------------------
  // Registration ceremony
  // ------------------------------------------------------------------
  getRegisterOptions: async (email: string, name: string): Promise<WebAuthnOptions> => {
    return fetcher(
      api.post('api/v1/auth/register/options', {
        json: { email, name },
        credentials: 'include',
      }),
      WebAuthnOptionsSchema,
    )
  },

  verifyRegistration: async (credential: unknown): Promise<LoginResponse> => {
    return fetcher(
      api.post('api/v1/auth/register/verify', {
        json: { credential },
        credentials: 'include',
      }),
      LoginResponseSchema,
    )
  },

  // ------------------------------------------------------------------
  // Login ceremony (usernameless)
  // ------------------------------------------------------------------
  getLoginOptions: async (): Promise<WebAuthnOptions> => {
    return fetcher(
      api.post('api/v1/auth/login/options', { credentials: 'include' }),
      WebAuthnOptionsSchema,
    )
  },

  verifyLogin: async (credential: unknown): Promise<LoginResponse> => {
    return fetcher(
      api.post('api/v1/auth/login/verify', {
        json: { credential },
        credentials: 'include',
      }),
      LoginResponseSchema,
    )
  },

  // ------------------------------------------------------------------
  // Passkey management (authenticated)
  // ------------------------------------------------------------------
  listPasskeys: async (): Promise<PasskeyListResponse> => {
    return fetcher(api.get('api/v1/auth/passkeys'), PasskeyListResponseSchema)
  },

  getAddPasskeyOptions: async (): Promise<WebAuthnOptions> => {
    return fetcher(
      api.post('api/v1/auth/passkeys/options', { credentials: 'include' }),
      WebAuthnOptionsSchema,
    )
  },

  verifyAddPasskey: async (credential: unknown): Promise<PasskeyCreatedResponse> => {
    return fetcher(
      api.post('api/v1/auth/passkeys/verify', {
        json: { credential },
        credentials: 'include',
      }),
      PasskeyCreatedResponseSchema,
    )
  },

  deletePasskey: async (passkeyId: string): Promise<void> => {
    await api.delete(`api/v1/auth/passkeys/${passkeyId}`)
  },

  // ------------------------------------------------------------------
  // Session
  // ------------------------------------------------------------------
  refresh: async (): Promise<RefreshResponse> => {
    return fetcher(api.post('api/v1/auth/refresh'), RefreshResponseSchema)
  },

  me: async (): Promise<MeResponse> => {
    return fetcher(api.get('api/v1/auth/me'), MeResponseSchema)
  },

  logout: async (): Promise<void> => {
    await api.post('api/v1/auth/logout')
  },
}
