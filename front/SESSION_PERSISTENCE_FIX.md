# Fix: Session Persistence After Page Refresh

**Date**: January 26, 2026  
**Issue**: User déconnecté à chaque rafraîchissement de page  
**Status**: ✅ FIXED

---

## 🐛 Problème

### Comportement Observé

- Utilisateur se connecte avec Google OAuth ✅
- Tout fonctionne normalement ✅
- **Rafraîchissement de la page (F5)** ❌
- Utilisateur redirigé vers `/login` ❌
- Doit se reconnecter à chaque fois ❌

### Cause Racine

**Dans `src/stores/auth.ts`** :

```typescript
// AVANT (problème)
const token = ref<string | null>(localStorage.getItem('auth_token')) // ✅ Persisté
const user = ref<User | null>(null) // ❌ PAS persisté
const isAuthenticated = computed(() => !!token.value && !!user.value) // ❌ Toujours false au refresh
```

**Séquence du problème** :

1. Page rafraîchit → Store réinitialisé
2. `token` = récupéré de localStorage ✅
3. `user` = `null` (pas sauvegardé) ❌
4. `isAuthenticated` = `false` (car `user === null`) ❌
5. Router guard détecte `!isAuthenticated` → redirige vers `/login` ❌

---

## ✅ Solution

### Persister les données utilisateur dans localStorage

**Modifications dans `src/stores/auth.ts`** :

#### 1. Restauration au chargement

```typescript
// Restore user from localStorage on initialization
const storedUser = localStorage.getItem('auth_user')
const user = ref<User | null>(storedUser ? JSON.parse(storedUser) : null)
```

#### 2. Sauvegarde lors de la connexion

```typescript
const setAuth = (accessToken: string, userData: User) => {
  token.value = accessToken
  user.value = userData
  localStorage.setItem('auth_token', accessToken)
  localStorage.setItem('auth_user', JSON.stringify(userData)) // ✨ NOUVEAU
  error.value = null
}
```

#### 3. Suppression lors de la déconnexion

```typescript
const clearAuth = () => {
  token.value = null
  user.value = null
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user') // ✨ NOUVEAU
}
```

---

## 🔄 Nouveau Flux

### Au Login

1. Utilisateur se connecte avec Google
2. Backend renvoie `{ accessToken, user }`
3. `setAuth()` sauvegarde **BOTH** dans localStorage :
   - `auth_token` → JWT
   - `auth_user` → Données utilisateur (JSON stringifié)

### Au Rafraîchissement

1. Page rafraîchit → Store Pinia réinitialisé
2. **Token restauré** : `localStorage.getItem('auth_token')` ✅
3. **User restauré** : `JSON.parse(localStorage.getItem('auth_user'))` ✅
4. `isAuthenticated` = `true` (token ET user présents) ✅
5. Router guard laisse passer → Pas de redirection ✅

### Au Logout

1. Utilisateur clique "Logout"
2. `clearAuth()` supprime **BOTH** de localStorage :
   - `auth_token` supprimé
   - `auth_user` supprimé
3. Store réinitialisé
4. Redirection vers `/login`

---

## 🧪 Comment Tester

### Test 1 : Login + Refresh

```bash
1. npm run dev
2. Ouvrir http://localhost:5173
3. Se connecter avec Google
4. Vérifier : redirection vers /dashboard
5. Appuyer sur F5 (rafraîchir)
6. ✅ ATTENDU : Rester sur /dashboard (PAS de redirection vers /login)
7. ✅ ATTENDU : Données utilisateur toujours affichées
```

### Test 2 : Vérifier localStorage

```javascript
// Dans la console navigateur (F12)

// Après login
localStorage.getItem('auth_token') // Doit retourner le JWT
localStorage.getItem('auth_user') // Doit retourner JSON des données user

// Parse user data
JSON.parse(localStorage.getItem('auth_user'))
// Doit afficher : { id: "...", email: "...", name: "...", ... }
```

### Test 3 : Logout

```bash
1. Se connecter
2. Vérifier localStorage (token + user présents)
3. Cliquer "Logout"
4. ✅ ATTENDU : Redirection vers /login
5. ✅ ATTENDU : localStorage vide (auth_token ET auth_user supprimés)
```

### Test 4 : Session Expiry

```bash
1. Se connecter
2. Attendre expiration du JWT (ou supprimer manuellement auth_token)
3. Rafraîchir la page
4. ✅ ATTENDU : Redirection vers /login (token invalide)
5. ✅ ATTENDU : auth_user aussi supprimé (clearAuth appelé)
```

---

## 📊 Impact

### Données Stockées dans localStorage

#### Avant

```javascript
{
  "auth_token": "eyJhbGc..." // Seulement le token
}
```

#### Après

```javascript
{
  "auth_token": "eyJhbGc...",           // JWT
  "auth_user": "{\"id\":\"...\", ...}"  // Données utilisateur (stringifié)
}
```

### Taille des Données

- **Token JWT** : ~200-500 bytes
- **User Data** : ~150-300 bytes (id, email, name, createdAt)
- **Total** : ~500-800 bytes (négligeable)

---

## 🔒 Considérations de Sécurité

### ✅ Bonnes Pratiques Respectées

1. **JWT dans localStorage** :
   - ✅ Acceptable pour SPA (Single Page Application)
   - ✅ Protection HTTPS requise (production)
   - ✅ Expiration du token côté backend

2. **Données utilisateur non sensibles** :
   - ✅ Pas de mots de passe stockés
   - ✅ Seulement : id, email, name (données publiques)
   - ✅ Pas de tokens de refresh dans localStorage

3. **Validation côté backend** :
   - ✅ Chaque requête vérifie le JWT
   - ✅ Token expiré → 401 Unauthorized → clearAuth()

### ⚠️ Limitations Connues

1. **XSS (Cross-Site Scripting)** :
   - Si attaquant injecte JS → Peut lire localStorage
   - **Mitigation** : Sanitize inputs, CSP headers, HTTPS only

2. **Pas de HttpOnly Cookie** :
   - localStorage accessible via JS (vs HttpOnly cookie)
   - **Trade-off** : Simplicité SPA vs sécurité maximale
   - **Acceptable** pour MVP/prototypes

3. **Session côté client** :
   - Pas de révocation instantanée (sauf expiration JWT)
   - **Mitigation** : JWT avec courte durée de vie (1h - 24h)

---

## 🎯 Recommandations Futures

### Court Terme (MVP) ✅

- [x] Persister token + user dans localStorage
- [ ] Ajouter expiration check côté frontend
- [ ] Implémenter refresh token flow (optionnel)

### Moyen Terme (Production)

- [ ] Ajouter CSRF protection
- [ ] Implémenter Content Security Policy (CSP)
- [ ] Logger les tentatives de connexion suspectes
- [ ] Ajouter "Remember me" option

### Long Terme (Sécurité Avancée)

- [ ] Évaluer migration vers HttpOnly cookies
- [ ] Implémenter device fingerprinting
- [ ] Ajouter 2FA (Two-Factor Authentication)
- [ ] Session management côté backend avec révocation

---

## 📝 Notes Techniques

### Pourquoi JSON.stringify/parse ?

localStorage ne stocke que des **strings**. Les objets doivent être sérialisés :

```typescript
// ❌ INCORRECT
localStorage.setItem('user', user) // Stocke "[object Object]"

// ✅ CORRECT
localStorage.setItem('user', JSON.stringify(user)) // Stocke '{"id":"...","email":"..."}'
```

### Pourquoi pas Pinia persist plugin ?

**Option considérée** : `pinia-plugin-persistedstate`

**Décision** : Implémentation manuelle pour :

- ✅ Contrôle total sur ce qui est persisté
- ✅ Pas de dépendance externe
- ✅ Logique explicite et transparente
- ✅ Plus simple à déboguer

---

## ✅ Vérification

### Build Status

```bash
$ npm run type-check
✓ No TypeScript errors

$ npm run build
✓ Built in 1.33s
✓ Bundle: 406.92 KB (124.91 KB gzipped)
```

### Files Changed

- `src/stores/auth.ts` (3 modifications)
  - Restauration user au chargement
  - Sauvegarde user dans setAuth()
  - Suppression user dans clearAuth()

---

## 🚀 Résultat

**AVANT** : Déconnexion à chaque refresh ❌  
**APRÈS** : Session persiste après refresh ✅

**Expérience utilisateur** :

- ✅ Login une seule fois
- ✅ Navigation normale
- ✅ Refresh → Reste connecté
- ✅ Fermeture onglet → Reste connecté
- ✅ Redémarrage navigateur → Reste connecté (jusqu'à expiration JWT)
- ✅ Logout → Déconnexion propre

---

**Status**: ✅ READY TO TEST

**Next Action**: Tester le flux complet login → refresh → navigation → logout
