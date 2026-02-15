# Quick Testing Guide - Google OAuth Login

## 🎯 What to Test

The Google OAuth login flow with automatic snake_case → camelCase transformation.

---

## ⚡ Quick Start

### 1. Prerequisites

```bash
# Ensure backend is running on configured port
# Check .env for VITE_API_BASE_URL

# Start frontend
npm run dev
```

### 2. Test Login Flow

1. Open browser: http://localhost:5173
2. Navigate to login page
3. Click "Login with Google"
4. Complete Google authentication
5. **Observe console** (F12) for any errors

---

## ✅ Expected Behavior

### Console (No Errors)

```
✓ No Zod validation errors
✓ No "accessToken is undefined" errors
✓ API response should show transformed keys (if logged)
```

### LocalStorage

```javascript
// Open DevTools → Application → Local Storage
localStorage.getItem('auth_token') // Should contain JWT
localStorage.getItem('user') // Should contain user data (if stored)
```

### UI

```
✓ User redirected to dashboard/home
✓ User profile displayed (name, avatar)
✓ Authenticated state active
```

---

## 🐛 What Could Go Wrong

### Scenario 1: Zod Validation Error

```
❌ Error: "accessToken" is required
```

**Cause**: Backend response not being transformed  
**Debug**:

```typescript
// In src/lib/api/client.ts, temporarily add:
console.log('Original response:', json)
console.log('Transformed:', camelCasedJson)
```

### Scenario 2: UUID Validation Error

```
❌ Error: "id" must be a valid UUID
```

**Cause**: Backend returning non-UUID user IDs  
**Fix Options**:

1. Backend converts IDs to UUID format (recommended)
2. Remove `.uuid()` from UserSchema in `src/lib/api/schemas/auth.ts`

### Scenario 3: Network Error

```
❌ NetworkError: Failed to fetch
```

**Cause**: Backend not running or wrong URL  
**Fix**: Check `VITE_API_BASE_URL` in `.env`

---

## 🔍 Debug Commands

### Check Transformation

```typescript
// In browser console after login attempt
// Check last API response
fetch('http://your-backend/auth/google', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: 'test' }),
})
  .then((r) => r.json())
  .then(console.log) // Should show snake_case keys
```

### Check Zod Schemas

```typescript
// Verify schemas expect camelCase
import { AuthResponseSchema } from '@/lib/api/schemas/auth'
console.log(AuthResponseSchema.shape)
// Should show: accessToken, user, etc. (camelCase)
```

---

## 📋 Test Checklist

### Pre-Test

- [ ] Backend running and accessible
- [ ] `.env` configured with correct `VITE_API_BASE_URL`
- [ ] Google OAuth credentials configured
- [ ] Frontend dev server running (`npm run dev`)

### During Test

- [ ] Google login button appears
- [ ] Clicking opens Google OAuth popup/redirect
- [ ] Google authentication succeeds
- [ ] Console shows no Zod errors
- [ ] Console shows no network errors

### Post-Test

- [ ] JWT token in localStorage
- [ ] User redirected to authenticated route
- [ ] User profile visible in UI
- [ ] Can access protected routes
- [ ] Can make authenticated API calls

---

## 🚀 Advanced Testing

### Test Other Endpoints

```bash
# After successful login, test:
# 1. Activities CRUD
# 2. Categories
# 3. Groups
# 4. Constraints
# 5. Insights

# All should work without Zod errors
```

### Test Edge Cases

```javascript
// Backend returns null for optional fields
{
  access_token: "jwt...",
  user: {
    id: "uuid",
    avatar_url: null,  // Should transform to avatarUrl: null
    created_at: "2024-01-25"
  }
}

// Backend returns nested arrays
{
  user_groups: [
    { group_id: "1", group_name: "Work" },
    { group_id: "2", group_name: "Personal" }
  ]
}
```

---

## 📊 Success Criteria

### ✅ Test Passes If:

1. No Zod validation errors in console
2. JWT token stored in localStorage
3. User redirected to authenticated route
4. User data displayed correctly in UI
5. All subsequent API calls work

### ❌ Test Fails If:

1. Zod validation error mentioning snake_case keys
2. "accessToken is undefined" error
3. Login flow hangs or fails silently
4. User not redirected after authentication
5. API calls fail with validation errors

---

## 🆘 Troubleshooting

### Problem: Still seeing snake_case errors

**Solution**:

1. Check `src/lib/api/client.ts` has `toCamelCase()` import
2. Verify `fetcher()` calls `toCamelCase(json)` before `schema.parse()`
3. Clear browser cache and localStorage
4. Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

### Problem: Transformation not applied

**Solution**:

1. Ensure you're using `fetcher()` wrapper, not raw `ky`
2. Check all API calls use `await fetcher(api.get(...), Schema)`
3. Verify `toCamelCase` is imported correctly

### Problem: Types don't match

**Solution**:

```bash
# Re-run type checking
npm run type-check

# If errors, check Zod schemas use camelCase keys
```

---

## 📞 Need Help?

### Check Documentation

- `SESSION_SUMMARY.md` - Complete session overview
- `CASING_TRANSFORMATION.md` - Transformation details
- `AGENTS.md` - Project standards

### Debug Steps

1. Check console for exact error message
2. Verify backend response format (Network tab)
3. Add temporary logging in `client.ts` fetcher
4. Check localStorage for stored data
5. Test with Postman/curl to isolate frontend/backend

---

**Last Updated**: January 26, 2026  
**Status**: Ready for Testing  
**Estimated Test Time**: 5-10 minutes
