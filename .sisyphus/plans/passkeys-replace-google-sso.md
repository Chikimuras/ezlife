# Plan: Replace Google SSO with Passkeys (WebAuthn)

## TL;DR
Remove all Google OAuth integration and replace with WebAuthn passkeys. Multi-user signup is open, login is usernameless (discoverable credentials), users can register multiple passkeys.

## Design Decisions
- **Library back**: `webauthn` (py-webauthn from Duo, MIT)
- **Library front**: `@simplewebauthn/browser` (MIT)
- **RP ID**: `local.ezlife.com` (dev), configurable via env
- **Expected origin**: `https://local.ezlife.com:8443` (dev)
- **Challenge storage**: signed cookie, 5min TTL (no Redis dep)
- **Resident keys**: required (usernameless login)
- **User verification**: required (biometric/PIN)
- **Multi-passkey**: yes (settings UI to manage)
- **Existing data**: wipe (no Google users to migrate)

## Schema Change
New table `webauthn_credentials`:
- `id` (UUID PK)
- `user_id` (FK users, CASCADE)
- `credential_id` (LargeBinary, unique, indexed)
- `public_key` (LargeBinary)
- `sign_count` (Integer, default 0)
- `transports` (JSON, list of strings)
- `device_name` (String, nullable)
- `created_at`, `last_used_at`

## Endpoints

### New
| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/v1/auth/register/options` | none | Returns CreationOptions + sets challenge cookie |
| POST | `/api/v1/auth/register/verify` | none | Verifies attestation, creates user + credential, issues JWT |
| POST | `/api/v1/auth/login/options` | none | Returns RequestOptions (no allow_credentials) + sets challenge cookie |
| POST | `/api/v1/auth/login/verify` | none | Verifies assertion, issues JWT |
| GET  | `/api/v1/auth/passkeys` | user | List user's passkeys |
| POST | `/api/v1/auth/passkeys/options` | user | Add new passkey: returns CreationOptions |
| POST | `/api/v1/auth/passkeys/verify` | user | Confirm new passkey |
| DELETE | `/api/v1/auth/passkeys/{id}` | user | Remove a passkey (refuses if last one) |

### Removed
- `POST /api/v1/login/google`

### Kept
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/logout-all`
- `GET /api/v1/auth/sessions`

## Frontend Changes
- Remove `vue3-google-login` dep + plugin
- Add `@simplewebauthn/browser`
- Rewrite `LoginView.vue`: single "Se connecter avec passkey" button
- New `RegisterView.vue`: email + name + "Créer mon compte"
- New route `/register`
- New `PasskeysSettings.vue` for managing passkeys (integrate into settings)
- Update `auth.ts` store: replace `loginWithGoogle` with `loginWithPasskey`, `registerWithPasskey`
- Update `lib/api/auth.ts`: replace `loginWithGoogle` with new methods

## Config Changes
Removed env vars:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `VITE_GOOGLE_CLIENT_ID`

New env vars:
- `WEBAUTHN_RP_ID` (default `localhost`)
- `WEBAUTHN_RP_NAME` (default `ezlife`)
- `WEBAUTHN_EXPECTED_ORIGIN` (default `http://localhost:5173`)

## Waves
1. **Backend foundation**: deps + config + model + migration + User relationship
2. **Backend service + endpoints**: webauthn_service.py, webauthn endpoints, remove Google service code
3. **Backend cleanup**: config env vars, tests update
4. **Frontend auth flow**: deps, LoginView, RegisterView, auth store, router
5. **Frontend settings**: PasskeysSettings.vue + integration
6. **Cleanup + tests**: i18n, full test suite

## Definition of Done
- [ ] User can register an account (email + name) and create a passkey
- [ ] User can log in usernameless (no email input on login page)
- [ ] User can add a second passkey from settings
- [ ] User can delete a passkey (except the last one)
- [ ] Refresh token flow still works
- [ ] No `google`/`Google`/`GOOGLE` references remaining in `api/app/` or `front/src/`
- [ ] `vue3-google-login` removed from `front/package.json`
- [ ] `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` removed from config + env files
- [ ] All tests pass (front + API)
- [ ] Manual smoke test: register → login → add second passkey → delete first → login with second
