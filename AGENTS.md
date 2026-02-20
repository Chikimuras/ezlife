# AGENTS.md — ezlife Monorepo

Monorepo with two independent projects: `api/` (Python/FastAPI) and `front/` (Vue 3/TypeScript).
Each has its own git repo, package manager, and sub-level `AGENTS.md` with full details.
**This file is the quick-reference. Defer to sub-level AGENTS.md for deep specifics.**

---

## 1. Build / Lint / Test Commands

### API (`api/`) — Python 3.12+, uv, FastAPI

```bash
# Working directory: api/

# Dependencies
uv sync                                    # Install all deps
uv add <pkg>                               # Add runtime dep
uv add --dev <pkg>                         # Add dev dep

# Run
uv run uvicorn app.main:app --reload       # Dev server (port 8000)
docker compose up --build                  # Full stack (app + Postgres)

# Test (pytest + pytest-asyncio, async auto-mode)
uv run pytest                              # All tests
uv run pytest tests/test_foo.py            # Single file
uv run pytest tests/test_foo.py::test_bar  # Single test
uv run pytest -s                           # With stdout
uv run pytest -k "keyword"                 # Filter by name

# Lint & Format
uv run ruff check .                        # Lint (rules: E, F, I, W, UP, B)
uv run ruff check . --fix                  # Lint + autofix
uv run black .                             # Format
uv run pre-commit run --all-files          # Run all hooks
```

### Frontend (`front/`) — TypeScript, Vue 3, Vite

```bash
# Working directory: front/

# Dependencies
npm install                                # Install deps

# Run
npm run dev                                # Dev server (Vite)
npm run build                              # Prod build (vue-tsc + vite build)
npm run preview                            # Preview prod build

# Test (Vitest, jsdom environment, globals enabled)
npm run test                               # Watch mode
npm run test:run                           # Single run (CI)
# Single file: npx vitest run src/path/to/file.test.ts
# Single test: npx vitest run -t "test name pattern"

# Lint & Format
npm run lint                               # ESLint --fix
npm run format                             # Prettier (src/)
npm run type-check                         # vue-tsc --noEmit
```

---

## 2. Code Style — API (Python)

- **Line length**: 88 chars (Ruff + Black)
- **Quotes**: Double quotes (`"`)
- **Indentation**: 4 spaces
- **Imports**: Auto-sorted by Ruff (isort rules). Order: stdlib, third-party, local.
- **Typing**: Mandatory on all function signatures. Use Python 3.12+ generics.
- **Pydantic**: V2 style (`model_config`, `field_validator`)
- **SQLAlchemy**: 2.0 style (`Mapped`, `mapped_column`)
- **Naming**: `snake_case` functions/vars, `PascalCase` classes, `UPPER_CASE` constants, `_private`
- **Error handling**: Always catch specific exceptions. Log with `loguru` BEFORE raising `HTTPException`.
- **Logging**: `from loguru import logger` — mandatory in all services/repos. See `api/AGENTS.md` for log levels.
- **Lockfile**: Never edit `uv.lock` manually — use `uv add/remove`.

---

## 3. Code Style — Frontend (TypeScript / Vue)

### Formatting (Prettier)
- **Semicolons**: None (`semi: false`)
- **Quotes**: Single quotes (`singleQuote: true`)
- **Print width**: 100
- **Tab width**: 2 spaces
- **Trailing commas**: All (`trailingComma: "all"`)

### TypeScript
- **Strict mode**: Enabled (`strict: true`, `noUnusedLocals`, `noUnusedParameters`)
- **`any` is forbidden.** No `as any`, `@ts-ignore`, `@ts-expect-error`.
- **Path alias**: `@/` maps to `src/`
- **Zod-first types**: Define Zod schema, infer type — never manually define API response interfaces.
  ```ts
  export const UserSchema = z.object({ id: z.string() })
  export type User = z.infer<typeof UserSchema>
  ```

### Vue Components
- **Always** `<script setup lang="ts">`
- **Script order**: Imports > Props/Emits > Composables/Stores > Reactive state > Lifecycle > Methods
- **Import order**: Vue core > Libraries > Local modules
- **Template**: kebab-case components (`<my-component>`), self-closing void elements
- **Props**: `defineProps<Props>()` generic syntax, defaults via `withDefaults`

### Naming
- **Files**: PascalCase components (`UserProfile.vue`), camelCase logic (`useAuth.ts`)
- **Variables/Functions**: camelCase
- **Constants**: UPPER_CASE
- **Composables**: `use` prefix (`useTheme`)
- **Stores**: `use` prefix + `Store` suffix (`useUserStore`)

### Tailwind CSS v4
- No `tailwind.config.js` — use CSS variables in `src/assets/styles/main.css` under `@theme`
- Dynamic classes: use `cn()` helper (clsx + tailwind-merge)

### API Client
- Never call `ky` directly in components. Use `fetcher()` wrapper from `src/lib/api/client.ts`.

### State (Pinia)
- Setup Stores only (function syntax), not Option Stores.

### i18n
- All UI text must use `vue-i18n` `t()` function. No hardcoded strings.
- Translation files: `src/lib/i18n/locales/{en,fr}.json`
- Keys: dot notation (`auth.login.button`)

---

## 4. Architecture

### API Structure (Clean Architecture)
```
api/app/
  api/v1/endpoints/   # Thin route handlers
  core/               # Config, security, deps, logging
  db/                 # Async DB session (asyncpg + SQLAlchemy 2.0)
  models/             # SQLAlchemy ORM models
  schemas/            # Pydantic DTOs
  services/           # Business logic
  main.py             # Entrypoint
```
- All routes under `/api/v1`
- Always set `response_model` on endpoints
- Use `Depends()` for DI (db sessions, auth, services)
- Migrations: Alembic (async mode)

### Frontend Structure
```
front/src/
  app/                # App-level setup, providers
  components/ui/      # Shadcn-vue primitives (own them, edit directly)
  components/features/# Domain-specific components
  composables/        # Reusable logic (hooks)
  lib/                # Utilities, API client, helpers
  lib/api/            # Ky client + Zod fetcher
  lib/i18n/           # i18n setup + locales
  stores/             # Pinia stores
  views/              # Page components (route-mapped)
```

---

## 5. Git Conventions

- **Commits**: Conventional Commits (enforced by pre-commit hook)
- **Format**: `type(scope): description` — present tense imperative
- **Types**: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`
- **Example**: `feat(auth): add Google OAuth2 login flow`
- Atomic commits — one logical change per commit
- Never commit secrets. Use `.env` + `pydantic-settings`. Keep `.env.example` in sync.

---

## 6. Agent Rules

1. **Verify before finishing**: Run `ruff check` (API) or `type-check` + `lint` (front) on changed files.
2. **Match existing patterns**: Check neighboring files before writing new code.
3. **Prefer edits over new files** unless adding a new module.
4. **No bare `except:`** (API). No `any` (front). No empty catch blocks.
5. **DB model changes require Alembic migration**.
6. **Logic changes require test cases**.
7. **Front design system**: Pastel feminine theme (lilac primary, sage green secondary, warm grays). See `front/AGENTS.md` section 4.5 for full palette, typography, component styles.
8. **Warn the user** if a requested change violates these conventions.
