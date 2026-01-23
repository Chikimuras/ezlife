# Agent Operational Guide (AGENTS.md)

This file documents the standards, patterns, and workflows for AI agents operating in this repository.
Follow these guidelines strictly to maintain codebase consistency and quality.

## 1. Project Context & Stack

- **Framework**: Vue 3 (Composition API, `<script setup>`)
- **Build Tool**: Vite
- **Language**: TypeScript (Strict Mode)
- **Styling**: Tailwind CSS v4 (Native CSS variables)
- **UI Library**: Shadcn-vue (Headless primitives + Tailwind)
- **State Management**: Pinia (Setup Stores)
- **API Client**: Ky.js + Zod (Type-safe fetching)
- **Auth**: Google OAuth2 (`vue3-google-login`)

## 2. Operational Commands

### Build & Development

- **Start Dev Server**: `npm run dev`
- **Production Build**: `npm run build` (Runs `vue-tsc` type checking first)
- **Preview Build**: `npm run preview`

### Verification

- **Type Check**: `npx vue-tsc --noEmit`
  - _Rule_: ALWAYS run this after making changes to `.ts` or `.vue` files to ensure type safety.
- **Linting**: `npm run lint` (ESLint)
- **Formatting**: `npm run format` (Prettier)
- **Pre-commit**: Automatically runs linting, formatting, and type-checking.

## 3. Code Style & Patterns

### Vue Components (`.vue`)

- **Syntax**: Always use `<script setup lang="ts">`.
- **Order**:
  1.  Imports (Vue -> Libs -> Local)
  2.  Props/Emits definitions
  3.  Composables/Store usage
  4.  Reactive state (`ref`, `computed`)
  5.  Lifecycle hooks
  6.  Methods/Handlers
- **Template**: Use kebab-case for components (`<my-component>`). Use self-closing tags for void elements.
- **Props**: Use `defineProps<Props>()` generic syntax. Defaults via `withDefaults`.
  ```typescript
  const props = withDefaults(
    defineProps<{
      variant?: 'default' | 'outline'
    }>(),
    {
      variant: 'default',
    },
  )
  ```

### TypeScript

- **Strict Mode**: Enabled. `any` is strictly forbidden.
- **Inference**: Prefer type inference where possible. Explicitly type function returns if complex.
- **Zod Integration**:
  - DO NOT manually define interfaces for API responses.
  - Define a Zod schema and infer the type:
    ```typescript
    export const UserSchema = z.object({ id: z.string() })
    export type User = z.infer<typeof UserSchema>
    ```

### Naming Conventions

- **Files**: PascalCase for components (`UserProfile.vue`), camelCase for logic (`useAuth.ts`, `apiClient.ts`).
- **Variables/Functions**: camelCase (`isLoading`, `fetchData`).
- **Constants**: UPPER_CASE for static configuration (`API_BASE_URL`).
- **Composables**: Prefix with `use` (`useTheme`).
- **Stores**: Prefix with `use` and Suffix with `Store` (`useUserStore`).

## 4. Architecture & Library Specifics

### API Layer (Ky + Zod)

- **Location**: `src/lib/api/`
- **Pattern**: NEVER call `ky` directly in components.
- **Fetcher**: Use the generic `fetcher` wrapper in `client.ts` which enforces Zod validation.
  ```typescript
  // Correct usage
  const data = await fetcher(api.get('users'), UserSchema)
  ```

### State Management (Pinia)

- **Syntax**: Use "Setup Stores" (function syntax), NOT Option Stores.
  ```typescript
  export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null) // State
    const isAuthenticated = computed(() => !!user.value) // Getter
    function login() { ... } // Action
    return { user, isAuthenticated, login }
  })
  ```
- **Persistence**: Handle persistence explicitly (e.g., `localStorage`) within actions, or use a plugin if configured.

### Styling (Tailwind v4)

- **Configuration**: NO `tailwind.config.js`. Use CSS variables in `src/assets/styles/main.css` under `@theme`.
- **Utility**: Use the `cn()` helper (clsx + tailwind-merge) for dynamic classes.
  ```vue
  <div :class="cn('bg-red-500', props.class)">
  ```

### Shadcn-vue Components

- **Location**: `src/components/ui/`
- **Modification**: These are "yours" to own. Modify the file directly to change styles; do not override via global CSS.

## 5. File Structure Guidelines

- `src/app/`: App-level setups, providers.
- `src/components/features/`: Complex domain-specific components.
- `src/components/ui/`: Reusable, dumb UI primitives (buttons, inputs).
- `src/composables/`: Reusable logic (hooks).
- `src/lib/`: Core utilities, API clients, helpers (vendor agnostic logic).
- `src/stores/`: Global state modules.
- `src/views/`: Page-level components mapped to routes.

## 6. Error Handling

- **API Errors**: Handle `HTTPError` from `ky`.
- **Validation Errors**: Handle `ZodError` when schema parsing fails.
- **UI Feedback**: Expose error states via reactive variables (`error` ref) in composables or stores to display in the UI.

## 7. Git & Workflow

- **Atomic Commits**: One logical change per commit.
- **Messages**: Present tense imperative ("Add feature", not "Added feature").
- **Pre-commit**: Ensure `npm run build` passes (this runs type checks).
