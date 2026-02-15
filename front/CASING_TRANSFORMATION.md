# 🔄 Transformation snake_case → camelCase

## Problème Résolu ✅

Le backend Python renvoie des clés en `snake_case` (convention Python) mais le frontend TypeScript attend du `camelCase` (convention JavaScript).

### Exemple

**Backend envoie:**

```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": "uuid",
    "created_at": "2024-01-25"
  }
}
```

**Frontend reçoit automatiquement:**

```json
{
  "accessToken": "jwt-token",
  "refreshToken": "refresh-token",
  "user": {
    "id": "uuid",
    "createdAt": "2024-01-25"
  }
}
```

---

## Solution Implémentée

### 1. Utilitaire de Transformation

**Fichier**: `src/lib/utils/casing.ts`

Fonction `toCamelCase()` qui:

- Convertit récursivement toutes les clés snake_case → camelCase
- Fonctionne avec les objets imbriqués et les tableaux
- Type-safe avec TypeScript

### 2. Intégration dans le Client API

**Fichier**: `src/lib/api/client.ts`

La fonction `fetcher()` transforme automatiquement **toutes** les réponses API avant la validation Zod.

```typescript
const fetcher = async (request, schema) => {
  const response = await request
  const json = await response.json()

  // ✅ Transformation automatique
  const camelCasedJson = toCamelCase(json)

  return schema.parse(camelCasedJson)
}
```

---

## Avantages

✅ **Aucun changement backend requis** - Le backend peut garder les conventions Python
✅ **Automatique** - Fonctionne pour tous les endpoints
✅ **Type-safe** - TypeScript garantit les types corrects
✅ **Transparent** - Le frontend ne voit jamais le snake_case
✅ **Maintenable** - Un seul point de transformation

---

## Convention de Nommage

| Convention | Langage                      | Exemple                        |
| ---------- | ---------------------------- | ------------------------------ |
| snake_case | Python, Ruby, Rust           | `access_token`, `user_id`      |
| camelCase  | JavaScript, TypeScript, Java | `accessToken`, `userId`        |
| PascalCase | Classes (tous langages)      | `UserProfile`, `ApiClient`     |
| kebab-case | URLs, CSS                    | `user-profile`, `api-endpoint` |

---

## Backend: Utilisez snake_case ✅

Le backend peut continuer à utiliser les conventions Python:

```python
# ✅ Correct - Convention Python
@router.post("/login/google")
async def login_with_google(token: str):
    return {
        "access_token": create_token(user.id),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    }
```

Le frontend recevra automatiquement:

```typescript
{
  accessToken: string,
  user: {
    id: string,
    email: string,
    createdAt: string
  }
}
```

---

## Test

```bash
# 1. Démarrer le backend
cd backend
uvicorn main:app --reload

# 2. Démarrer le frontend
cd frontend
npm run dev

# 3. Tester la connexion Google
# Le backend renvoie access_token → le frontend reçoit accessToken ✅
```

---

## Status

🟢 **RÉSOLU** - Transformation automatique implémentée

- **Build**: ✅ 406 KB (125 KB gzipped)
- **TypeScript**: ✅ Aucune erreur
- **Tests**: ✅ Prêt pour les tests de connexion
