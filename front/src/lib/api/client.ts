import ky from 'ky'

export const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  hooks: {
    beforeRequest: [
      request => {
        // Example: Add token if exists
        const token = localStorage.getItem('auth_token')
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      }
    ]
  }
})
