# Automatic Token Refresh Implementation

**Date**: January 26, 2026  
**Feature**: Session persistante illimitée avec refresh automatique  
**Status**: ✅ IMPLÉMENTÉ

---

## 🎯 Problème Résolu

### Comportement Avant

- ✅ Session persiste après refresh de page
- ❌ Après expiration du JWT (ex: 1h-24h) → Déconnexion automatique
- ❌ Utilisateur doit se reconnecter manuellement

### Comportement Après

- ✅ Session persiste après refresh de page
- ✅ Token rafraîchi **automatiquement** avant expiration
- ✅ **Session illimitée** tant que l'utilisateur est actif
- ✅ Pas de déconnexion intempestive

---

## 🏗️ Architecture

### Système à 3 Composants

```
┌─────────────────────────────────────────────────────────────┐
│  1. JWT Utilities (src/lib/utils/jwt.ts)                    │
│     - Décodage du JWT                                        │
│     - Lecture de l'expiration (exp claim)                    │
│     - Calcul du temps restant                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Token Refresh Composable (useTokenRefresh)              │
│     - Schedule refresh 5 min avant expiration                │
│     - Appelle authStore.refreshToken()                       │
│     - Re-schedule après chaque refresh                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Auth Store (authStore)                                   │
│     - Callback onTokenUpdated()                              │
│     - Notifie useTokenRefresh à chaque mise à jour           │
│     - Sauvegarde nouveau token dans localStorage             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Fichiers Créés/Modifiés

### Créés (2 fichiers)

#### 1. `src/lib/utils/jwt.ts`

Utilitaires pour manipuler les JWT :

```typescript
// Décoder un JWT et extraire le payload
decodeJWT(token: string): JWTPayload | null

// Obtenir le timestamp d'expiration (en ms)
getTokenExpirationTime(token: string): number | null

// Vérifier si le token est expiré
isTokenExpired(token: string): boolean

// Temps restant avant expiration (en ms)
getTimeUntilExpiration(token: string): number
```

**Exemple** :

```typescript
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
const payload = decodeJWT(token)
// { exp: 1738000000, iat: 1737996400, sub: "user-id", ... }

const timeLeft = getTimeUntilExpiration(token)
// 3600000 (= 1 heure en millisecondes)
```

#### 2. `src/composables/useTokenRefresh.ts`

Composable pour gérer le refresh automatique :

```typescript
export const useTokenRefresh = () => {
  const {
    isRefreshing, // État du refresh en cours
    startTokenRefreshCycle, // Démarrer le cycle
    stopTokenRefreshCycle, // Arrêter le cycle
    refreshToken, // Forcer un refresh manuel
  } = useTokenRefresh()
}
```

**Fonctionnement** :

1. `startTokenRefreshCycle()` lit le JWT actuel
2. Calcule : `refreshIn = timeUntilExpiry - 5 minutes`
3. Programme un `setTimeout(refreshToken, refreshIn)`
4. Quand le timeout se déclenche → appelle `authStore.refreshToken()`
5. Backend renvoie un nouveau JWT
6. authStore notifie via `onTokenUpdated(newToken)`
7. **Re-schedule** automatiquement avec le nouveau token
8. Cycle infini ✅

---

### Modifiés (2 fichiers)

#### 3. `src/stores/auth.ts`

Ajout du système de callbacks :

**Nouveautés** :

```typescript
// Tableau de callbacks
const onTokenUpdatedCallbacks: Array<(token: string) => void> = []

// S'abonner aux mises à jour du token
const onTokenUpdated = (callback: (token: string) => void) => {
  onTokenUpdatedCallbacks.push(callback)
}

// Notifier tous les listeners
const notifyTokenUpdated = (newToken: string) => {
  onTokenUpdatedCallbacks.forEach((cb) => cb(newToken))
}
```

**Modifications** :

- `setAuth()` → Appelle `notifyTokenUpdated()` après sauvegarde
- `refreshToken()` → Appelle `notifyTokenUpdated()` après refresh
- Export de `onTokenUpdated` dans le return

#### 4. `src/App.vue`

Démarrage du cycle au chargement :

**Ajout** :

```typescript
import { useTokenRefresh } from '@/composables/useTokenRefresh'

const { startTokenRefreshCycle } = useTokenRefresh()

onMounted(async () => {
  // ... existing code ...

  if (authStore.token) {
    const isValid = await authStore.fetchCurrentUser()
    if (isValid) {
      startTokenRefreshCycle() // ✨ NOUVEAU
    }
  }
})
```

---

## 🔄 Flux Complet

### Au Login

```
1. Utilisateur se connecte avec Google
   ↓
2. Backend renvoie JWT (exp: now + 1h)
   ↓
3. authStore.setAuth() sauvegarde token + user
   ↓
4. authStore notifie onTokenUpdated()
   ↓
5. useTokenRefresh reçoit le nouveau token
   ↓
6. Schedule refresh dans 55 minutes (1h - 5min)
   ↓
7. Console log: "Scheduling token refresh in 3300s (55min)"
```

### Au Refresh de Page

```
1. Page rafraîchit → App.vue re-monte
   ↓
2. authStore restaure token + user depuis localStorage
   ↓
3. App.vue appelle fetchCurrentUser() (vérifie token valide)
   ↓
4. Si valide → startTokenRefreshCycle()
   ↓
5. useTokenRefresh lit exp du token
   ↓
6. Schedule refresh avant expiration
```

### Au Refresh Automatique

```
1. setTimeout se déclenche (55 min après login)
   ↓
2. useTokenRefresh.refreshToken() est appelé
   ↓
3. authStore.refreshToken() fait POST /auth/refresh
   ↓
4. Backend vérifie refresh token (httpOnly cookie)
   ↓
5. Backend renvoie nouveau JWT (exp: now + 1h)
   ↓
6. authStore.refreshToken() sauvegarde nouveau token
   ↓
7. authStore notifie onTokenUpdated(newToken)
   ↓
8. useTokenRefresh re-schedule dans 55 min
   ↓
9. CYCLE SE RÉPÈTE INFINIMENT ♾️
```

### Au Logout

```
1. Utilisateur clique "Logout"
   ↓
2. authStore.logout() appelle backend
   ↓
3. Backend invalide refresh token (supprime cookie)
   ↓
4. authStore.clearAuth() supprime token + user
   ↓
5. useTokenRefresh détecte token === null
   ↓
6. Arrête le cycle (clearTimeout)
   ↓
7. Redirection vers /login
```

---

## ⚙️ Configuration

### Temps de Refresh

**Constante** : `REFRESH_BEFORE_EXPIRY_MS` dans `useTokenRefresh.ts`

```typescript
const REFRESH_BEFORE_EXPIRY_MS = 5 * 60 * 1000 // 5 minutes
```

**Exemples** :

| JWT Expiration | Refresh Scheduled | Marge de Sécurité |
| -------------- | ----------------- | ----------------- |
| 1 heure        | 55 minutes        | 5 minutes         |
| 24 heures      | 23h 55min         | 5 minutes         |
| 7 jours        | 6j 23h 55min      | 5 minutes         |

**Pourquoi 5 minutes ?**

- ✅ Suffisant pour gérer réseau lent
- ✅ Protège contre clock skew (décalage horloge)
- ✅ Utilisateur ne voit jamais l'expiration

---

## 🧪 Comment Tester

### Test 1 : Vérifier le Scheduling

```bash
1. npm run dev
2. Ouvrir console (F12)
3. Se connecter avec Google
4. Chercher dans console :
   ✅ "Scheduling token refresh in XXXs"
   ✅ "expiresIn: YYYs"
```

**Exemple de log** :

```
[INFO] Scheduling token refresh
  refreshIn: 3300s  (= 55 minutes)
  expiresIn: 3600s  (= 1 heure)
```

### Test 2 : Forcer un Refresh Rapide

**Modifier temporairement** `REFRESH_BEFORE_EXPIRY_MS` :

```typescript
// Dans src/composables/useTokenRefresh.ts
const REFRESH_BEFORE_EXPIRY_MS = 10 * 1000 // 10 secondes au lieu de 5 min
```

**Tester** :

```bash
1. Se connecter
2. Attendre 10 secondes
3. Console doit afficher :
   ✅ "Refreshing access token"
   ✅ "Token refreshed successfully"
   ✅ "Scheduling token refresh in XXXs" (nouveau cycle)
```

### Test 3 : Vérifier localStorage

**Console navigateur** :

```javascript
// Voir le token
localStorage.getItem('auth_token')

// Décoder le JWT
const token = localStorage.getItem('auth_token')
const payload = JSON.parse(atob(token.split('.')[1]))
console.log(payload)
// { exp: 1738000000, iat: 1737996400, sub: "...", ... }

// Calculer expiration
const expMs = payload.exp * 1000
const now = Date.now()
const timeLeftMin = Math.round((expMs - now) / 60000)
console.log(`Token expires in ${timeLeftMin} minutes`)
```

### Test 4 : Session Longue Durée

```bash
1. Se connecter
2. Laisser l'application ouverte pendant 2+ heures
3. Naviguer dans l'app de temps en temps
4. Console doit montrer refreshes réguliers :
   ✅ "Token refreshed successfully" (toutes les ~55 min)
5. ✅ ATTENDU : Aucune déconnexion
```

### Test 5 : Backend Down During Refresh

**Scénario** : Backend tombe pendant un refresh

```bash
1. Se connecter
2. Arrêter le backend
3. Attendre que le refresh se déclenche
4. Console doit montrer :
   ❌ "Token refresh failed, logging out"
5. ✅ ATTENDU : Redirection vers /login
```

---

## 🔒 Sécurité

### Refresh Token (HttpOnly Cookie)

**Backend doit** :

- ✅ Envoyer refresh token en **httpOnly cookie** (inaccessible au JS)
- ✅ Vérifier le refresh token à chaque `/auth/refresh`
- ✅ Rotation du refresh token (optionnel mais recommandé)
- ✅ Expiration longue (7-30 jours)

**Frontend** :

- ✅ N'a jamais accès au refresh token (httpOnly)
- ✅ Envoie automatiquement le cookie via `credentials: 'include'`
- ✅ Stocke seulement l'access token (JWT court)

### Protection XSS

**Même si attaquant injecte JS** :

- ❌ Peut lire access token dans localStorage (durée courte)
- ✅ **NE PEUT PAS** lire refresh token (httpOnly cookie)
- ✅ Access token expire rapidement (1h-24h)
- ✅ Refresh token protégé côté backend

### Révocation

**Backend peut révoquer** :

- Supprimer refresh token de la DB
- Prochain refresh échouera
- Frontend déconnecte automatiquement

---

## 📊 Performance

### Impact Réseau

**Par session de 8 heures** :

- JWT exp: 1 heure
- Refreshes: ~8 requests
- Taille: ~500 bytes par request
- **Total**: ~4 KB sur 8h (négligeable)

### Impact CPU

**setTimeout** :

- Exécution une fois toutes les ~55 min
- Impact CPU: < 0.01%
- **Négligeable**

---

## 🎯 Avantages

### Utilisateur

✅ **Jamais déconnecté** pendant utilisation active  
✅ Session persiste même après fermeture/réouverture navigateur  
✅ Pas de prompt de reconnexion intempestif  
✅ Expérience fluide

### Développeur

✅ Système automatique (aucune action utilisateur)  
✅ Code centralisé (1 composable)  
✅ Logs détaillés pour debugging  
✅ Gestion d'erreur robuste

### Sécurité

✅ Access token courte durée (limite exposition XSS)  
✅ Refresh token httpOnly (protection maximale)  
✅ Révocation côté backend possible  
✅ Rotation de tokens (optionnel)

---

## 🚨 Limitations

### Session "Infinie"

**Note importante** : La session n'est **PAS réellement infinie**.

**Limites** :

1. **Refresh token expire** (backend config: 7-30 jours typiquement)
2. **Backend peut révoquer** (logout autre appareil, changement mot de passe, etc.)
3. **Navigateur fermé longtemps** (si > expiration refresh token)

**Résultat** :

- ✅ Session persiste tant que refresh token valide
- ✅ Utilisateur actif quotidiennement → Jamais déconnecté
- ❌ Utilisateur inactif 30 jours → Doit se reconnecter

### Refresh Échoue

**Si le refresh échoue** :

- Utilisateur déconnecté immédiatement
- Redirection vers `/login`
- **Cause possible** :
  - Backend down
  - Refresh token révoqué
  - Problème réseau

**Mitigation** :

- Retry logic dans client.ts (hooks afterResponse)
- Fallback vers erreur utilisateur si retry échoue

---

## 📝 Backend Requirements

### Endpoint Required

**POST /api/v1/auth/refresh**

**Request** :

```http
POST /api/v1/auth/refresh
Cookie: refresh_token=<httpOnly-cookie>
```

**Response Success (200)** :

```json
{
  "access_token": "eyJhbGci..."
}
```

**Response Error (401)** :

```json
{
  "error": "invalid_refresh_token",
  "message": "Refresh token expired or invalid"
}
```

### Backend Logic

```python
@router.post("/auth/refresh")
async def refresh_token(request: Request):
    # 1. Lire refresh token depuis httpOnly cookie
    refresh_token = request.cookies.get("refresh_token")

    # 2. Vérifier validité
    if not refresh_token or not verify_refresh_token(refresh_token):
        raise HTTPException(401, "Invalid refresh token")

    # 3. Générer nouveau access token
    new_access_token = create_access_token(user_id, expires_in=3600)

    # 4. (Optionnel) Rotation du refresh token
    new_refresh_token = create_refresh_token(user_id, expires_in=2592000)

    # 5. Retourner
    response = JSONResponse({"access_token": new_access_token})
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, secure=True)
    return response
```

---

## ✅ Vérification

### Build Status

```bash
$ npm run type-check
✓ No TypeScript errors

$ npm run build
✓ Built in 1.35s
✓ Bundle: 408.35 KB (125.42 KB gzipped)
```

### Files Changed

1. ✅ `src/lib/utils/jwt.ts` (créé)
2. ✅ `src/composables/useTokenRefresh.ts` (créé)
3. ✅ `src/stores/auth.ts` (modifié - callbacks)
4. ✅ `src/App.vue` (modifié - start cycle)

---

## 🚀 Résultat Final

**AVANT** ❌ :

- Session expire après 1h-24h
- Déconnexion automatique
- Utilisateur doit se reconnecter

**APRÈS** ✅ :

- Token rafraîchi automatiquement
- Session persiste indéfiniment (tant que refresh token valide)
- **Aucune déconnexion intempestive**
- Expérience utilisateur fluide

---

**Status**: ✅ READY TO TEST

**Next Action**:

1. Tester le login
2. Vérifier les logs dans console
3. Attendre ~55 min (ou modifier `REFRESH_BEFORE_EXPIRY_MS` à 10s)
4. Observer le refresh automatique
5. Laisser l'app ouverte plusieurs heures → Aucune déconnexion

**Session maintenant illimitée** 🎉
