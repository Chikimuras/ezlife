import { z } from 'zod'

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string(),
  createdAt: z.string().optional(),
})

export const LoginResponseSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string().optional(), // Optional if backend sends it in httpOnly cookie
  user: UserSchema,
})

export const RefreshResponseSchema = z.object({
  accessToken: z.string(),
})

export const MeResponseSchema = z.object({
  user: UserSchema,
})

export type User = z.infer<typeof UserSchema>
export type LoginResponse = z.infer<typeof LoginResponseSchema>
export type RefreshResponse = z.infer<typeof RefreshResponseSchema>
export type MeResponse = z.infer<typeof MeResponseSchema>
