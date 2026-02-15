import ky, { type KyResponse } from 'ky'
import { type ZodSchema, ZodError } from 'zod'
import { toCamelCase } from '@/lib/utils/casing'

let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

const addRefreshSubscriber = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback)
}

export const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  retry: {
    limit: 3,
    methods: ['get', 'put', 'head', 'delete', 'options', 'trace'],
    statusCodes: [408, 413, 429, 500, 502, 503, 504],
    backoffLimit: 3000,
  },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
    afterResponse: [
      async (request, _options, response) => {
        if (response.status === 401) {
          const originalRequest = request.clone()

          if (isRefreshing) {
            return new Promise((resolve) => {
              addRefreshSubscriber((token: string) => {
                originalRequest.headers.set('Authorization', `Bearer ${token}`)
                resolve(ky(originalRequest))
              })
            })
          }

          isRefreshing = true

          try {
            const refreshResponse = await ky.post('api/v1/auth/refresh', {
              prefixUrl: import.meta.env.VITE_API_BASE_URL,
              credentials: 'include',
              retry: 0,
            })

            const { accessToken } = await refreshResponse.json<{ accessToken: string }>()

            localStorage.setItem('auth_token', accessToken)
            isRefreshing = false
            onRefreshed(accessToken)

            originalRequest.headers.set('Authorization', `Bearer ${accessToken}`)
            return ky(originalRequest)
          } catch (error) {
            isRefreshing = false
            localStorage.removeItem('auth_token')
            window.location.href = '/login'
            throw error
          }
        }

        return response
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

  const camelCasedJson = toCamelCase(json)

  try {
    return schema.parse(camelCasedJson)
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = new Error('API Response Validation Failed')
      ;(validationError as any).name = 'ValidationError'
      ;(validationError as any).context = 'API Response Validation'
      ;(validationError as any).zodError = error
      ;(validationError as any).responseData = json
      throw validationError
    }
    throw error
  }
}
