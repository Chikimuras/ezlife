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

- **Type Check**: `npm run type-check`
  - _Rule_: ALWAYS run this after making changes to `.ts` or `.vue` files to ensure type safety.
- **Linting**: `npm run lint` (ESLint)
- **Formatting**: `npm run format` (Prettier)
- **Testing**: `npm run test` (Vitest in watch mode) or `npm run test:run` (Single run)
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

## 4.5. Design System

### Color Palette (Pastel Feminine Theme)

**Primary Color: Lilac/Mauve** (Purple tones - main accent)

- `primary-50`: #faf5ff (Lightest lilac)
- `primary-100`: #f3e8ff
- `primary-200`: #e9d5ff
- `primary-300`: #d8b4fe
- `primary-400`: #c084fc
- `primary-500`: #a855f7 (Base primary)
- `primary-600`: #9333ea (Primary for text/icons)
- `primary-700`: #7e22ce
- `primary-800`: #6b21a8
- `primary-900`: #581c87 (Darkest)

**Secondary Color: Sage Green** (Calming green tones)

- `secondary-50`: #f5f7f5
- `secondary-100`: #e8ede8
- `secondary-200`: #d1ddd1
- `secondary-300`: #aac4aa
- `secondary-400`: #88ac88
- `secondary-500`: #6b9670 (Base secondary)
- `secondary-600`: #547a59 (Secondary for text/icons)
- `secondary-700`: #44624a
- `secondary-800`: #39503d
- `secondary-900`: #304234

**Neutral: Warm Grays**

- `gray-50`: #fafaf9 (Backgrounds)
- `gray-100`: #f5f5f4 (Light backgrounds)
- `gray-200`: #e7e5e4 (Borders)
- `gray-300`: #d6d3d1
- `gray-400`: #a8a29e
- `gray-500`: #78716c
- `gray-600`: #57534e (Secondary text)
- `gray-700`: #44403c
- `gray-800`: #292524
- `gray-900`: #1c1917 (Primary text)

### Typography

- **Font Family**:
  - Sans: `Inter, system-ui, sans-serif`
  - Display: `Plus Jakarta Sans, Inter, sans-serif`
- **Text Colors**:
  - Primary text: `text-gray-900`
  - Secondary text: `text-gray-600`
  - Muted text: `text-gray-500`
  - Link text: `text-primary-600`
- **Font Sizes**:
  - Heading 1: `text-2xl font-semibold`
  - Heading 2: `text-xl font-semibold`
  - Heading 3: `text-lg font-medium`
  - Body: `text-sm`
  - Body Small: `text-xs`
  - Caption: `text-xs text-gray-500`

### Spacing & Layout

- **Container**: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- **Section Padding**: `py-6` (large), `py-4` (medium), `py-2` (small)
- **Card Padding**: `p-4` (large), `p-3` (medium), `p-2` (small)
- **Gaps**:
  - Grid: `gap-4` (large), `gap-3` (medium), `gap-2` (small)
  - Flex: `space-x-2`, `space-y-2`

### Border Radius (Soft, Feminine Feel)

- Small: `rounded-md` (0.375rem)
- Medium: `rounded-lg` (0.5rem)
- Large: `rounded-xl` (0.75rem)
- Full: `rounded-full`

### Shadows

- Small: `shadow-sm` (Subtle elevation)
- Medium: `shadow-md` (Cards, modals)
- Large: `shadow-lg` (Buttons, important elements)
- Extra Large: `shadow-xl` (Hero elements, hover states)

### Button Styles

**Modern, compact buttons with subtle shadows and smooth transitions.**

**Primary Button** (Call-to-action)

```vue
<button class="px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 rounded-lg shadow-sm hover:shadow transition-colors">
```

**Secondary Button** (Less emphasis)

```vue
<button class="px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors">
```

**Outline Button**

```vue
<button class="px-3 py-1.5 text-sm font-medium text-gray-700 border border-gray-200 hover:border-gray-300 hover:bg-gray-50 rounded-md transition-colors">
```

**Ghost Button** (Minimal)

```vue
<button class="px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors">
```

**Destructive Button**

```vue
<button class="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg shadow-sm hover:shadow transition-colors">
```

**Size Variants:**

- **Default**: `px-4 py-2 text-sm` (most common)
- **Small**: `px-3 py-1.5 text-sm` (compact)
- **Large**: `px-5 py-2.5 text-base` (emphasis)

### Card Styles

**Feature Card** (Landing page style)

```vue
<div class="bg-white border border-gray-100 rounded-lg p-4 shadow-sm hover:shadow transition-shadow">
  <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center mb-3">
    <!-- Icon here -->
  </div>
  <h3 class="text-base font-semibold text-gray-900 mb-2">Title</h3>
  <p class="text-sm text-gray-600 leading-relaxed">Description</p>
</div>
```

**Content Card**

```vue
<div class="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
  <!-- Content -->
</div>
```

### Form Elements

**Input**

```vue
<input
  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
/>
```

**Label**

```vue
<label class="block text-sm font-medium text-gray-700 mb-1">Label</label>
```

**Select**

```vue
<select class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all">
```

**Checkbox**

```vue
<input
  type="checkbox"
  class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
/>
```

### Table Styles

**Modern borderless tables with alternating row colors**

```vue
<table class="w-full">
  <thead>
    <tr>
      <th class="px-3 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">Header</th>
    </tr>
  </thead>
  <tbody class="[&_tr:nth-child(even)]:bg-primary-50">
    <tr class="hover:bg-gray-50/50 transition-colors">
      <td class="px-3 py-3 text-sm text-gray-900">Cell</td>
    </tr>
  </tbody>
</table>
```

**Design principles:**

- **No borders**: Clean, modern look without visual clutter
- **Alternating rows**: Even rows have subtle lilac background (`bg-primary-50`)
- **Hover state**: Rows highlight on hover (`hover:bg-gray-50/50`)
- **Header style**: Uppercase, smaller text, semibold for clear hierarchy

### Badge Styles

```vue
<span
  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-primary-100 text-primary-700"
>
  Badge Text
</span>
```

### Loading States

**Spinner** (Use text color for theme)

```vue
<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
```

**Skeleton**

```vue
<div class="animate-pulse bg-gray-200 rounded-lg h-4 w-full"></div>
```

### Background Decorations

**Gradient Background** (Hero sections)

```vue
<div class="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
```

**SVG Decorative Elements** (Soft organic shapes)

```vue
<svg class="absolute opacity-20" viewBox="0 0 400 400">
  <circle cx="200" cy="100" r="120" fill="url(#gradient1)" />
  <defs>
    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color: #e9d5ff; stop-opacity: 1" />
      <stop offset="100%" style="stop-color: #c084fc; stop-opacity: 0.6" />
    </linearGradient>
  </defs>
</svg>
```

### Icons

- Primary icon color: `text-primary-600`
- Secondary icon color: `text-secondary-600`
- Neutral icon color: `text-gray-600`
- Icon sizes: `w-4 h-4` (small), `w-6 h-6` (medium), `w-8 h-8` (large)

### Transitions

- Default: `transition-colors` (200ms)
- All properties: `transition-all` (200ms)
- Transform: `transform hover:scale-105` (buttons, cards)
- Shadow: `hover:shadow-xl` (emphasis)

### Design Principles

1. **Soft & Feminine**: Use rounded corners, pastel colors, gentle shadows
2. **Breathing Space**: Generous padding and margins
3. **Subtle Interactions**: Smooth transitions, gentle hover effects
4. **Visual Hierarchy**: Clear typography scale, color contrast
5. **Consistency**: Reuse design tokens, follow patterns

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

## 8. Internationalization (i18n)

- **Library**: Use `vue-i18n` for translations.
- **Location**: `src/lib/i18n/locales/` for translation files. `src/lib/i18n/index.ts` for setup.
- **Usage**: Use the `t` function in components for translations.
  ```vue
  <template>
    <p>{{ t('welcome_message') }}</p>
  </template>
  ```
- **Keys**: Use dot notation for nested keys (`auth.login.button`).
- **Variables**: Use interpolation for dynamic content.
  ```vue
  <p>{{ t('greeting', { name: userName }) }}</p>
  ```
- **Adding Languages**: Add new JSON files in `locales/` and update the i18n setup to include the new language.
- **Fallbacks**: Ensure a default language is set for missing translations.
- **Plurals**: Use i18n pluralization features for count-based messages.
  ```vue
  <p>{{ t('items', { count: itemCount }) }}</p>
  ```
- All text content must be internationalized; hardcoded strings are not allowed.
- **Testing**: Regularly test the application in different languages to ensure proper rendering and layout.
