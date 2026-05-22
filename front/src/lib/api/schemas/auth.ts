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

/**
 * Server-issued WebAuthn ceremony options.
 *
 * py-webauthn's `options_to_json` already emits the camelCase, base64url-encoded
 * shape that @simplewebauthn/browser expects, so we accept any shape here and
 * let the browser library validate it.
 */
export const WebAuthnOptionsSchema = z.record(z.string(), z.unknown())

export const PasskeySummarySchema = z.object({
  id: z.string().uuid(),
  deviceName: z.string().nullable(),
  createdAt: z.string(),
  lastUsedAt: z.string().nullable(),
})

export const PasskeyListResponseSchema = z.object({
  passkeys: z.array(PasskeySummarySchema),
})

export const PasskeyCreatedResponseSchema = z.object({
  passkey: PasskeySummarySchema,
})

export type User = z.infer<typeof UserSchema>
export type LoginResponse = z.infer<typeof LoginResponseSchema>
export type RefreshResponse = z.infer<typeof RefreshResponseSchema>
export type MeResponse = z.infer<typeof MeResponseSchema>
export type WebAuthnOptions = z.infer<typeof WebAuthnOptionsSchema>
export type PasskeySummary = z.infer<typeof PasskeySummarySchema>
export type PasskeyListResponse = z.infer<typeof PasskeyListResponseSchema>
export type PasskeyCreatedResponse = z.infer<typeof PasskeyCreatedResponseSchema>
