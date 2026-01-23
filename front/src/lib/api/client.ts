import ky, { type KyResponse } from 'ky'
import type { ZodSchema } from 'zod'

export const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  hooks: {
    beforeRequest: [
      (request) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
  },
})

export const fetcher = async <T>(
  request: Promise<KyResponse>,
  schema: ZodSchema<T>,
): Promise<T> => {
  const response = await request
  const json = await response.json()
  return schema.parse(json)
}
