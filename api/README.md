# Mon Vrai Projet

FastAPI backend for activity tracking and time management.

## Features

- 🔐 Google OAuth authentication
- 📊 Activity tracking with categories and groups
- 📅 Time-based activity management
- 🔄 Excel import/export functionality
- 🛡️ RFC 7807 compliant error handling

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: OAuth2 + JWT
- **Package Management**: uv
- **Deployment**: Docker + Docker Compose

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mon-vrai-projet
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the application:
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

## Development

### Run Locally

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn app.main:app --reload
```

### Code Quality

```bash
# Run linting
uv run ruff check .

# Format code
uv run black .

# Run tests
uv run pytest
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Error Codes**: [docs/error-codes.md](docs/error-codes.md)

## Architecture

```
app/
├── api/v1/endpoints/  # API routes
├── core/              # Core configuration, security, logging
├── db/                # Database session management
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas (DTOs)
├── services/          # Business logic layer
├── repositories/      # Data access layer
└── exceptions.py      # Custom exception classes
```

## Error Handling

This API follows [RFC 7807](https://tools.ietf.org/html/rfc7807) for standardized error responses.

All errors return this format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error summary",
  "detail": "Detailed explanation",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/resource"
}
```

See [Error Codes Documentation](docs/error-codes.md) for a complete reference.

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass and code is formatted
4. Submit a pull request

## License

[License Type] - See LICENSE file for details
