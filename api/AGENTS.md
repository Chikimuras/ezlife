# Agentic Guidelines for mon-vrai-projet

This file guides AI agents (and humans) on how to work effectively in this repository.
It defines the source of truth for build commands, code style, and architectural patterns.

## 1. Environment & Build

### Package Management
This project uses **uv** for all package management.
- **Install dependencies**: `uv sync`
- **Add dependency**: `uv add <package>` (use `--dev` for dev dependencies)
- **Run commands**: `uv run <command>`

### Docker
- **Build**: `docker build . -t app`
- **Run Stack**: `docker compose up --build`
- **Architecture**: Multi-stage build (Builder -> Runner) using `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
- **Orchestration**: `uv` handles venvs inside containers.

### Testing
We use **pytest** with **pytest-asyncio**.
- **Run all tests**: `uv run pytest`
- **Run single test file**: `uv run pytest tests/test_example.py`
- **Run single test case**: `uv run pytest tests/test_example.py::test_specific_case`
- **Run with output**: `uv run pytest -s`

### Linting & Formatting
We use **Ruff** for linting/sorting and **Black** for formatting (standard).
- **Check code**: `uv run ruff check .`
- **Format code**: `uv run black .`
- **Git Hooks**: Pre-commit is configured. Run `uv run pre-commit run --all-files` to verify manually.

---

## 2. Code Style & Conventions

### Python Version
- Target: **Python 3.12+**
- Use modern features: Type hints (generic aliases), f-strings, match statements.

### Formatting (Enforced by Ruff)
- **Line Length**: 88 characters.
- **Quotes**: Double quotes (`"`) for strings.
- **Indentation**: 4 spaces.
- **Imports**: Sorted automatically (Isort rules via Ruff).

### Typing
- **Strictness**: High. All function signatures must be typed.
- **Pydantic**: Use Pydantic V2 (`model_config`, `field_validator`).
- **SQLAlchemy**: Use modern 2.0 style (`Mapped`, `mapped_column`).

```python
# GOOD
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes/Models**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private**: `_leading_underscore`

### Error Handling
- Use **FastAPI `HTTPException`** for API errors.
- Never use bare `except:` blocks. Always catch specific exceptions.
- Log errors before raising HTTP exceptions if internal debugging is needed.

---

## 3. Architecture & Patterns

### Project Structure (Clean Architecture)
```
app/
├── api/v1/endpoints/  # API Routes (thin layer)
├── core/              # Config, Security, Deps
├── db/                # Database setup (AsyncSession)
├── models/            # SQLAlchemy Models (Data Layer)
├── schemas/           # Pydantic Models (DTO Layer)
├── services/          # Business Logic (Complex operations)
└── main.py            # Entrypoint
```

### Database (Async)
- **Driver**: `asyncpg`
- **ORM**: SQLAlchemy 2.0 Async
- **Session**: Dependency Injection via `get_db`.
- **Migrations**: Alembic (Async mode).

### API Design
- **Versioning**: All routes go under `/api/v1`.
- **Response Models**: Always define `response_model` in decorators.
- **Dependency Injection**: Use `Depends()` for services, user context, and DB sessions.

### Git Conventions (Enforced)
- **Format**: Conventional Commits
- **Types**: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`.
- **Example**: `feat(auth): implement oauth2 login flow`

---

## 4. Agent Behavior Rules

### 1. Safety First
- **Never** modify `uv.lock` manually. Use `uv add/remove`.
- **Never** commit secrets. Use `.env` and `pydantic-settings`.
- **Always** run `uv run ruff check` before finishing a task.

### 2. Implementation Strategy
- **Plan**: Check `AGENTS.md` and existing code styles first.
- **Atomic Changes**: Small, focused edits. One logical change per commit.
- **Verify**: If you change logic, add a test case. If you change DB models, create a migration.

### 3. File Operations
- Prefer **editing** existing files over creating new ones unless adding a new module.
- Keep `__init__.py` files clean; avoid circular imports.

### 4. Communication
- If a requested change violates these rules, **warn the user** before proceeding.
- When creating new files, ensure they are properly exported/imported in the module system.
