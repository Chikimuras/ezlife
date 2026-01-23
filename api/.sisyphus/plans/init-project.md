# Project Initialization Plan: Modern FastAPI + uv + Git Master

## 1. Directory Structure Setup (Clean Architecture)
We will create the following structure manually (using `mkdir`):

```
.
├── .github/
│   └── workflows/          # CI/CD pipelines (future)
├── .husky/                 # Git hooks
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/  # API Routes
│   │       └── api.py      # Router aggregation
│   ├── core/
│   │   ├── config.py       # Pydantic Settings
│   │   ├── security.py     # OAuth2 / JWT logic
│   │   └── deps.py         # DI Container
│   ├── db/
│   │   ├── base.py         # SQLAlchemy Base
│   │   └── session.py      # Async Engine
│   ├── models/             # DB Models
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # Business Logic
│   └── main.py             # Entrypoint
├── tests/                  # Pytest-asyncio suite
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile              # Multi-stage with uv
├── pyproject.toml          # uv + Ruff config
├── uv.lock
└── README.md
```

## 2. Tooling Configuration

### A. Package Management (`uv`)
- Initialize project: `uv init`
- Add dependencies:
  - Runtime: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `pydantic-settings`, `python-jose` (for OAuth2), `httpx` (for Google Auth)
  - Dev: `pytest`, `pytest-asyncio`, `ruff`, `pre-commit`, `husky`

### B. Git Master Setup (Atomic Commits)
1.  **Husky**: Install and configure `commit-msg` hook.
2.  **Commitlint**: Add `@commitlint/config-conventional` via node (if available) OR use a Python equivalent/regex check in pre-commit.
    *Decision*: Since this is a Python project, we will use `pre-commit` with `conventional-pre-commit` hook to avoid Node.js dependency just for linting, UNLESS you prefer the Node ecosystem standard.
    *Plan*: Use `pre-commit` framework for everything to keep it Python-native.
3.  **Ruff**: Configure as a pre-commit hook (lint + format).

### C. Docker & Orchestration
- **Dockerfile**: Multi-stage build using `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
- **Docker Compose**: Service definition for:
  - `app`: The FastAPI app
  - `db`: PostgreSQL 16
- **Orchestration**: `uv` will be used inside the container to manage venvs.

## 3. Implementation Steps

1.  **Scaffold**: Create directories and empty files.
2.  **Config**: Write `pyproject.toml` (Ruff, pytest) and `pre-commit-config.yaml`.
3.  **Dependencies**: Run `uv add ...` commands.
4.  **Core Code**:
    - `app/core/config.py`: Settings class.
    - `app/db/session.py`: Async engine.
    - `app/main.py`: Basic health check.
5.  **Git Setup**: Initialize git, install hooks.
6.  **Docker**: Write Dockerfile and compose.

## 4. Verification
- Run `uv sync` to ensure lockfile is valid.
- Run `pre-commit run --all-files` to verify hooks.
- Build Docker image: `docker build .`
