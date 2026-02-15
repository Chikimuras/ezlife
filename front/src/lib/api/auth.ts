import { api, fetcher } from './client'
import {
  LoginResponseSchema,
  RefreshResponseSchema,
  MeResponseSchema,
  type LoginResponse,
  type RefreshResponse,
  type MeResponse,
} from './schemas/auth'

export const authApi = {
  loginWithGoogle: async (googleToken: string): Promise<LoginResponse> => {
    return fetcher(
      api.post('api/v1/login/google', {
        json: { token: googleToken },
      }),
      LoginResponseSchema,
    )
  },

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
