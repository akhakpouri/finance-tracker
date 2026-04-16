# Personal Finance Tracker

## Project Overview

A full-stack personal finance tracker built as a **monorepo** containing a **FastAPI** (Python) backend API and a **TypeScript** frontend application. This is a learning project designed to translate existing Go and C# architectural patterns into idiomatic Python while building something with real depth — not a toy CRUD app.

## Developer Context

- **Background**: Experienced in Go (current) and C# (prior). Strong grasp of OOP, layered architecture, repository pattern, and typed systems.
- **Goal**: First Python application. Learn FastAPI and Python idioms by mapping familiar patterns (repositories, services, handlers, DTOs) into the Python ecosystem.
- **Preference**: Start with class-based patterns that feel familiar (repositories as classes, services as classes), then refactor toward more Pythonic approaches over time as comfort grows.

## Tech Stack

### Backend (api/)

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **ORM**: SQLAlchemy (async) with SQLModel or raw SQLAlchemy models
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Auth**: JWT (python-jose or PyJWT) + bcrypt for password hashing
- **Validation**: Pydantic v2 (built into FastAPI)
- **Testing**: pytest + FastAPI TestClient + test database
- **Config**: Pydantic Settings (environment-based)

### Frontend (web/)

- **Language**: TypeScript
- **Framework**: TBD — evaluating React (Next.js), Angular, or Vue.js (Nuxt). Decision pending.
- **Considerations**: Angular maps closest to the C#/OOP mindset (built-in DI, services, opinionated structure). React/Next.js has the larger ecosystem and more FastAPI tutorial overlap. Vue/Nuxt is the middle ground.

## Architecture

Layered architecture mirroring Go/C# conventions:

```
Routers (Handlers) → Services → Repositories → Database
            ↕               ↕
        Schemas (DTOs)    Models (Entities)
```

- **Models**: SQLAlchemy ORM classes representing database tables.
- **Schemas**: Pydantic models for request/response validation (the DTO equivalent).
- **Repositories**: Data access layer. Encapsulate all database queries. One repository per aggregate root.
- **Services**: Business logic layer. Orchestrate repositories, enforce rules, perform calculations.
- **Routers**: HTTP layer. Parse requests, call services, return responses. No business logic here.
- **Dependencies**: FastAPI's `Depends()` for injecting services, database sessions, and the authenticated user.

## Project Structure

Monorepo with `api/` and `web/` as sibling directories, each fully self-contained with their own dependency manifests. Neither is nested inside the other — they can be built and deployed independently.

```
finance-tracker/
├── README.md
├── claude.md
├── .gitignore
│
├── api/                                   # Python FastAPI backend
│   ├── pyproject.toml                     # Python dependencies, metadata, tool config
│   ├── alembic.ini
│   ├── .env                              # local env vars (gitignored)
│   ├── .env.example                      # committed template showing required env vars
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py                   # shared fixtures (test db, test client, auth helpers)
│   │   ├── test_users.py
│   │   ├── test_accounts.py
│   │   └── ...
│   └── src/
│       └── app/
│           ├── __init__.py
│           ├── main.py                   # FastAPI app factory, middleware, lifespan
│           ├── config/
│           │   ├── __init__.py
│           │   ├── settings.py           # Pydantic Settings class (env binding)
│           │   └── database.py           # async engine, session factory
│           ├── models/
│           │   ├── __init__.py
│           │   ├── user.py
│           │   ├── account.py
│           │   ├── transaction.py
│           │   ├── category.py
│           │   └── budget.py
│           ├── schemas/
│           │   ├── __init__.py
│           │   ├── user.py               # UserCreate, UserUpdate, UserResponse
│           │   ├── account.py
│           │   ├── transaction.py
│           │   └── ...
│           ├── repositories/
│           │   ├── __init__.py
│           │   ├── base.py               # generic base repo (CRUD methods)
│           │   ├── user.py               # user-specific queries
│           │   ├── account.py
│           │   └── ...
│           ├── services/
│           │   ├── __init__.py
│           │   ├── auth.py               # registration, login, token logic
│           │   ├── user.py
│           │   └── ...
│           ├── routers/
│           │   ├── __init__.py
│           │   ├── auth.py
│           │   ├── user.py
│           │   └── ...
│           ├── dependencies/
│           │   ├── __init__.py
│           │   ├── database.py           # get_db session dependency
│           │   └── auth.py               # get_current_user dependency
│           └── common/
│               ├── __init__.py
│               ├── exceptions.py         # custom exception classes
│               └── responses.py          # response envelope helpers
│
├── web/                                   # TypeScript frontend (framework TBD)
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.local                        # frontend env vars (API base URL, etc.)
│   ├── .env.example
│   └── src/
│       └── ...                           # framework-specific structure (determined after framework choice)
│
└── docs/                                  # shared documentation (optional)
    └── ...
```

### Structure Decisions

- **Monorepo with sibling directories.** `api/` and `web/` sit side by side at the repo root. Avoids nesting one inside the other, which creates deployment and build-tool headaches. Each directory is independently buildable and deployable.
- **Shared files at the root.** `claude.md`, `README.md`, and `.gitignore` live at the repo root since they describe the whole project. Each app has its own `.env` files for different config needs (API needs database credentials, frontend needs the API base URL).
- **`src/` layout in `api/`** chosen over flat layout. Prevents accidental imports from the working directory and forces proper package installation. Mirrors the explicit module boundaries familiar from Go and C#.
- **`pyproject.toml`** is the API's single project manifest. Holds dependencies, project metadata, and tool configuration (pytest, linting, formatting). Managed via a package manager (`uv` recommended for speed, `poetry` as the established alternative).
- **`config/`** is a directory (not a single file) because the project will accumulate multiple config concerns: database settings, JWT/auth settings, and eventually Redis/Celery config. Each gets its own module within the package.
- **`dependencies/`** is the FastAPI-specific DI layer. Houses all `Depends()` callables — database session provider, authenticated user extractor, etc. Kept separate from services to prevent circular imports, which is a common pain point in Python when services need sessions that need config.
- **`common/`** holds cross-cutting concerns: the response envelope helper, custom exception classes, shared constants. Named `common` rather than `utils` to signal "shared plumbing" and discourage it from becoming a junk drawer.
- **`repositories/base.py`** will contain a generic base class with `get_by_id`, `get_all`, `create`, `update`, `delete`. Entity-specific repositories inherit and extend it. Similar to a generic repository pattern in C#.
- **`schemas/`** uses Pydantic model inheritance for variants of each entity: `UserCreate` (input for registration), `UserUpdate` (partial updates), `UserResponse` (what the API returns). Keeps request and response shapes explicit.
- **`web/` structure is deferred** until a frontend framework is chosen. The internal `src/` layout will follow that framework's conventions (e.g. Next.js pages/app directory, Angular modules, Vue composables).

## Domain Model

### Entities & Fields

**User**
- `id` (UUID, PK)
- `email` (string, unique)
- `hashed_password` (string)
- `first_name` (string)
- `last_name` (string)
- `is_active` (boolean)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Account**
- `id` (UUID, PK)
- `user_id` (UUID, FK → User)
- `name` (string) — e.g. "Chase Checking", "Emergency Savings"
- `account_type` (enum: `checking`, `savings`, `credit_card`, `cash`)
- `balance` (decimal)
- `currency` (string) — default "USD"
- `is_active` (boolean)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Transaction**
- `id` (UUID, PK)
- `account_id` (UUID, FK → Account)
- `category_id` (UUID, FK → Category)
- `transaction_type` (enum: `income`, `expense`, `transfer`)
- `amount` (decimal)
- `description` (string)
- `transaction_date` (date)
- `notes` (string, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Category**
- `id` (UUID, PK)
- `user_id` (UUID, FK → User, nullable) — null means system default
- `name` (string)
- `category_type` (enum: `income`, `expense`)
- `is_system` (boolean) — redundant with null `user_id` but simplifies queries
- `created_at` (timestamp)

**Budget**
- `id` (UUID, PK)
- `user_id` (UUID, FK → User)
- `category_id` (UUID, FK → Category)
- `limit_amount` (decimal)
- `period` (enum: `monthly`, `weekly`)
- `start_date` (date) — anchors when the budget cycle begins
- `is_active` (boolean)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Relationships

- User → many Accounts
- User → many Categories (plus system defaults where `user_id` is null)
- User → many Budgets
- Account → many Transactions
- Category → many Transactions
- Category → many Budgets

### Entity Design Decisions

- **UUIDs over auto-increment integers** for primary keys. Safer for a multi-client API — IDs are unpredictable and can be generated client-side if needed.
- **`account_type`, `transaction_type`, `category_type`, `period`** are modeled as Python `Enum` classes mapped to PostgreSQL native enums via Alembic.
- **Categories have a nullable `user_id`**. When null, the category is a system default (groceries, rent, utilities). When populated, it's user-created. The `is_system` flag makes querying easier without checking for null.
- **Transfers are modeled as transactions**, not a separate entity. A transfer between accounts creates two transaction records (one expense from the source, one income to the destination) linked by business logic in the service layer. Consider adding a `transfer_id` field later to explicitly link paired transfer transactions.
- **Budgets tie a user to a category with a spending limit.** The service layer calculates "amount spent in current period" by querying transactions against that category within the date window derived from `start_date` + `period`.
- **`balance` on Account is a denormalized field.** It gets updated by the service layer when transactions are created/updated/deleted. The source of truth is the sum of transactions, but the cached balance avoids expensive aggregation on every read.
- **`decimal` for monetary amounts.** Never use float for money. In SQLAlchemy, use `Numeric(precision=12, scale=2)`. In Pydantic schemas, use `Decimal`.

## Phased Roadmap

### Phase 1 — Foundation
- Project structure and folder layout
- Database connection (async SQLAlchemy + PostgreSQL)
- Alembic migration setup
- Config management via Pydantic Settings
- User entity wired end-to-end (model → schema → repo → service → router)
- Health check endpoint
- Error handling middleware

### Phase 2 — Authentication & Authorization
- User registration and login endpoints
- JWT token issuance and validation
- Password hashing (bcrypt)
- `get_current_user` dependency for route protection
- All subsequent routes require authentication

### Phase 3 — Core Domain
- Accounts CRUD (scoped to authenticated user)
- Categories CRUD (system defaults + user-created)
- Transactions CRUD with filtering (date range, category, account, amount)
- Pagination on list endpoints
- Pydantic validators (positive amounts, valid dates, etc.)

### Phase 4 — Business Logic
- Budget system: set monthly limits per category, calculate spending vs. limits
- Dashboard/summary endpoint: account balances, monthly spending by category, budget status
- Account-to-account transfers (atomic, wrapped in DB transaction)

### Phase 5 — API Maturity
- Cursor-based or offset pagination as a reusable pattern
- Composable sorting and filtering via query parameters
- Structured logging
- Consistent API response envelope (success/error shape)
- Integration tests with TestClient and test database
- OpenAPI docs enrichment (examples, descriptions, tags)

### Phase 6 — Frontend Application
- Choose TypeScript framework (React/Next.js, Angular, or Vue/Nuxt)
- Scaffold `web/` directory with framework conventions
- Auth flow: login/register pages, JWT token storage, protected routes
- Core UI: accounts list, transaction list with filters, add/edit transaction forms
- Dashboard: account balances overview, spending by category, budget progress
- API client layer: typed HTTP client consuming the FastAPI backend

### Phase 7 — Stretch Goals
- Recurring/scheduled transactions
- CSV import/export
- Rate limiting
- Redis caching
- Background tasks (Celery or FastAPI background tasks)

## Coding Conventions

- **Type hints everywhere.** Coming from Go and C#, lean into Python's type system. All function signatures, return types, and variables should be annotated.
- **Async by default.** Use `async def` for route handlers, service methods, and repository methods. Use async SQLAlchemy sessions.
- **One file per concern.** Don't pile multiple routers or models into one file. Keep it modular.
- **Schemas are not models.** Keep Pydantic schemas (DTOs) and SQLAlchemy models (entities) strictly separated, even when they look similar.
- **No business logic in routers.** Routers parse and delegate. Services decide. Repositories fetch.
- **Dependency injection via `Depends()`.** Wire database sessions, services, and auth into route functions declaratively.
- **Consistent error responses.** Use FastAPI's `HTTPException` with standard status codes and a consistent error body shape.
- **Migrations are not optional.** Every schema change goes through Alembic. No manual table edits.

## Response Envelope (Target)

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

## Key Python/FastAPI Concepts to Learn

- `Depends()` for dependency injection (equivalent to C# DI container / Go middleware)
- Pydantic model inheritance for schema variants (Create, Update, Response)
- SQLAlchemy relationship loading strategies (lazy, eager, selectin)
- Alembic autogenerate for migrations
- `asynccontextmanager` for database session lifecycle
- FastAPI's automatic OpenAPI spec generation

## Project Memory System

Project knowledge is tracked in `docs/project-notes/`:

| File | Purpose |
|------|---------|
| `bugs.md` | Bug log with root causes and fixes |
| `decisions.md` | Architectural decision records (ADRs) |
| `facts.md` | Project config, constants, and reference info |
| `issues.md` | Work log with GitHub issue references |

### Memory-Aware Protocols

**Before proposing architectural changes:**
- Check `docs/project-notes/decisions.md` for existing decisions.
- Verify the proposed approach doesn't conflict with past choices.

**When encountering errors or bugs:**
- Search `docs/project-notes/bugs.md` for similar issues.
- Apply known fixes if found.
- Document new bugs and solutions when resolved.

**When looking up project configuration:**
- Check `docs/project-notes/facts.md` for credentials, ports, URLs, connection strings, and other configuration.
- Prefer documented facts over assumptions.