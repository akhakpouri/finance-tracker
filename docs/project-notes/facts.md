# Project Facts

Key configuration values, constants, and reference info. Check here before assuming defaults.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI (Python 3.12+) |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | JWT (python-jose or PyJWT) + bcrypt |
| Validation | Pydantic v2 |
| Testing | pytest + FastAPI TestClient |
| Config | Pydantic Settings (env-based) |
| Package manager | uv (preferred) or poetry |
| Frontend | TypeScript, framework TBD |

## Conventions

- Type hints on all function signatures, return types, and variables
- Async by default (`async def` for handlers, services, repositories)
- One file per concern
- Schemas (Pydantic DTOs) strictly separated from Models (SQLAlchemy entities)
- Dependency injection via FastAPI `Depends()`
- Every schema change goes through Alembic migrations

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/finance` |
| SECRET_KEY | JWT signing key | (generate a secure random value) |
| DEBUG | Enable debug mode | `true` / `false` |
| APP_NAME | Application name | `Finance Tracker` |
| API_PREFIX | API route prefix | `/api/v1` |

## Domain Enums

- **AccountType:** checking, savings, credit_card, cash
- **TransactionType:** income, expense, transfer
- **CategoryType:** income, expense
- **BudgetPeriod:** monthly, weekly
