export interface JWTPayload {
  exp?: number
  iat?: number
  sub?: string
  [key: string]: unknown
}

export const decodeJWT = (token: string): JWTPayload | null => {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    const payloadPart = parts[1]
    if (!payloadPart) {
      return null
    }

    const decoded = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

export const getTokenExpirationTime = (token: string): number | null => {
  const payload = decodeJWT(token)
  return payload?.exp ? payload.exp * 1000 : null
}

export const isTokenExpired = (token: string): boolean => {
  const expTime = getTokenExpirationTime(token)
  if (!expTime) return true
  return Date.now() >= expTime
}

export const getTimeUntilExpiration = (token: string): number => {
  const expTime = getTokenExpirationTime(token)
  if (!expTime) return 0
  return Math.max(0, expTime - Date.now())
}
