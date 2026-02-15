# Activity & Time Tracker

> Tracker d'activité et de temps ultra-personnalisable pour suivre et analyser votre quotidien personnel et professionnel.

Une application moderne pour enregistrer, suivre et obtenir des insights sur vos activités quotidiennes. Conçue pour simplifier et automatiser ce qui était auparavant géré manuellement sur Google Sheets, avec des rapports journaliers, hebdomadaires, mensuels et annuels.

## 🎯 Vision

Remplacer les tableurs Google Sheets complexes par une interface intuitive et automatisée qui permet de :

- **Logger rapidement** toutes vos activités (perso & pro)
- **Personnaliser** les catégories et métriques selon vos besoins
- **Analyser** vos habitudes avec des insights multi-périodes
- **Visualiser** votre temps et productivité

## ✨ Fonctionnalités

- 🔐 **Authentification Google OAuth2** - Connexion rapide et sécurisée
- 📊 **Insights multi-temporels** - Journaliers, hebdomadaires, mensuels, annuels
- 🎨 **Ultra personnalisable** - Adaptez l'application à vos besoins spécifiques
- ⚡ **Performance** - Interface réactive et temps de chargement optimisé
- 🌐 **Progressive Web App** (à venir) - Utilisable hors-ligne

## 🛠️ Stack Technique

### Frontend

- **Framework** : [Vue 3](https://vuejs.org/) avec Composition API (`<script setup>`)
- **Build Tool** : [Vite](https://vitejs.dev/)
- **Langage** : TypeScript (Strict Mode)
- **Styling** : [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Components** : [Shadcn-vue](https://www.shadcn-vue.com/)
- **State Management** : [Pinia](https://pinia.vuejs.org/) (Setup Stores)
- **Routing** : [Vue Router](https://router.vuejs.org/)
- **HTTP Client** : [Ky](https://github.com/sindresorhus/ky)
- **Validation** : [Zod](https://zod.dev/)
- **Icons** : [Lucide Vue Next](https://lucide.dev/)
- **i18n** : Vue I18n + Lingui

### Outils de Développement

- **Linting** : ESLint
- **Formatting** : Prettier
- **Type Checking** : TypeScript via `vue-tsc`
- **Git Hooks** : Husky + lint-staged
- **Package Manager** : npm

## 🚀 Démarrage Rapide

### Prérequis

- Node.js >= 18.x
- npm >= 9.x

### Installation

```bash
# Cloner le dépôt
git clone <repository-url>
cd mon-vrai-projet-front

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

### Configuration

Créez un fichier `.env` à la racine du projet :

```env
VITE_API_BASE_URL=https://your-api-url.com
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### Développement

```bash
# Lancer le serveur de développement
npm run dev

# Ouvrir http://localhost:5173
```

### Build de Production

```bash
# Vérifier les types + build
npm run build

# Prévisualiser le build
npm run preview
```

## 📁 Structure du Projet

```
src/
├── app/                  # Configuration app-level (providers)
├── assets/               # Ressources statiques (styles, images)
├── components/
│   ├── features/        # Composants métier complexes
│   └── ui/              # Primitives UI réutilisables (Shadcn)
├── composables/         # Hooks Vue réutilisables
├── lib/
│   ├── api/            # Client API (Ky + Zod)
│   └── utils/          # Utilitaires (cn, helpers)
├── router/             # Configuration du routage
├── stores/             # Stores Pinia (state global)
├── views/              # Pages/vues mappées aux routes
├── App.vue             # Composant racine
└── main.ts             # Point d'entrée
```

## 🧪 Scripts Disponibles

```bash
# Développement
npm run dev              # Serveur de développement

# Build
npm run build            # Build de production (avec type checking)
npm run preview          # Prévisualiser le build

# Qualité de Code
npm run lint             # Linter (auto-fix)
npm run format           # Formatter avec Prettier
npm run type-check       # Vérification TypeScript

# Git Hooks
npm run prepare          # Installer Husky (auto après install)
```

## 🔒 Sécurité & Authentification

L'application utilise **Google OAuth2** pour l'authentification :

1. L'utilisateur se connecte via le bouton Google
2. Le token Google est envoyé au backend
3. Le backend valide et retourne un JWT
4. Le JWT est stocké dans `localStorage` et attaché aux requêtes via un hook Ky

### Protection des Routes

- Les routes sont protégées via navigation guards dans `router/index.ts`
- L'état d'authentification est géré par le store Pinia `useAuthStore`

## 🎨 Styling & Theming

### Tailwind CSS v4

Cette application utilise **Tailwind v4** avec une approche basée sur les variables CSS natives :

- **Pas de `tailwind.config.js`** - Configuration via `@theme` dans `src/assets/styles/main.css`
- **Utilitaire `cn()`** - Fusion intelligente de classes (clsx + tailwind-merge)

```vue
<script setup>
import { cn } from '@/lib/utils/cn'
</script>

<template>
  <div :class="cn('bg-primary text-white', props.className)">
    <!-- Content -->
  </div>
</template>
```

### Composants Shadcn-vue

Les composants UI sont dans `src/components/ui/`. Modifiez-les directement - ils sont "yours to own".

## 📝 Conventions de Code

### Vue Components

- Toujours utiliser `<script setup lang="ts">`
- Ordre des sections : Imports → Props/Emits → Composables → State → Lifecycle → Methods
- Template en kebab-case : `<my-component />`

### TypeScript

- **Mode strict activé** - `any` est strictement interdit
- Privilégier l'inférence de type
- Définir les types via Zod quand possible :

```typescript
export const UserSchema = z.object({ id: z.string(), name: z.string() })
export type User = z.infer<typeof UserSchema>
```

### API Layer

**Ne jamais appeler `ky` directement dans les composants**. Utilisez le wrapper `fetcher` :

```typescript
import { api, fetcher } from '@/lib/api/client'

const data = await fetcher(api.get('users'), UserSchema)
```

### Pinia Stores

Utiliser la syntaxe **Setup Stores** (fonction, pas options) :

```typescript
export const useMyStore = defineStore('my-store', () => {
  const state = ref(0) // State
  const double = computed(() => state.value * 2) // Getter
  function increment() {
    state.value++
  } // Action

  return { state, double, increment }
})
```

## 🧑‍💻 Workflow de Développement

### Pre-commit Hooks

Chaque commit déclenche automatiquement :

1. **Linting** (ESLint avec auto-fix)
2. **Formatting** (Prettier)
3. **Type checking** (vue-tsc)

### Commits

- Messages en impératif présent : `"Add feature"` (pas `"Added"`)
- Commits atomiques : un changement logique par commit

### Pull Requests

1. Créer une branche depuis `main`
2. Faire vos changements
3. Vérifier que `npm run build` passe
4. Créer une PR avec description claire

## 🐛 Debugging

### Erreurs de Type

```bash
# Vérifier les erreurs TypeScript
npm run type-check
```

### Erreurs API

- Vérifiez la console navigateur pour les erreurs HTTP (Ky)
- Vérifiez les erreurs de validation Zod

## 🗺️ Roadmap

- [ ] 📊 Dashboard principal avec graphiques
- [ ] ⏱️ Timer pour tracking en temps réel
- [ ] 📂 Catégories personnalisables
- [ ] 📈 Exports de données (CSV, PDF)
- [ ] 🌙 Mode sombre
- [ ] 📱 Application mobile (PWA)
- [ ] 🔔 Notifications et rappels
- [ ] 🤖 Suggestions automatiques basées sur l'historique
- [ ] 📊 Rapports visuels avancés
- [ ] 🔄 Synchronisation multi-appareils

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence privée.

## 👨‍💻 Auteur

Développé avec ❤️ pour simplifier le tracking d'activité quotidien.

---

**Note** : Ce projet est en développement actif. Les fonctionnalités sont ajoutées progressivement.
