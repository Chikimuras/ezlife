import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { z } from 'zod'
import { api, fetcher } from '@/lib/api/client'

const LoginResponseSchema = z.object({
  token: z.string(),
  user: z.object({
    id: z.string(),
    email: z.string().email(),
    name: z.string(),
  }),
})

type LoginResponse = z.infer<typeof LoginResponseSchema>

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<LoginResponse['user'] | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const loginWithGoogle = async (googleToken: string) => {
    try {
      const response = await fetcher(
        api.post('api/v1/login/google', {
          json: { token: googleToken },
        }),
        LoginResponseSchema,
      )

      token.value = response.token
      user.value = response.user
      localStorage.setItem('auth_token', response.token)

      return response
    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    token,
    user,
    isAuthenticated,
    loginWithGoogle,
    logout,
  }
})
