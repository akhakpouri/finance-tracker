# Personal Finance Tracker

## Project Overview

A full-stack personal finance tracker built as a **multi-module Go monorepo** with a **Go** backend API and a **TypeScript** frontend. The data layer is extracted into a shared module so multiple backend processes — the HTTP API today, a background worker later — can reuse the same models and repositories. This is a real application with domain depth, not a toy CRUD app.

## Developer Context

- **Background**: Experienced in Go (primary) and C# (prior). Strong grasp of OOP, layered architecture, the repository pattern, and typed systems.
- **Goal**: Build a non-trivial, well-structured Go application end to end — clean module boundaries, a shared data layer, an HTTP API, and an eventual background worker — while practicing idiomatic Go.
- **Preference**: Start with the familiar repository/service/handler layering (interfaces defined producer-side, in the shared module) and refactor toward more idiomatic Go (e.g. consumer-defined interfaces) as comfort grows. The developer writes the code; assistance is guidance, review, and structure unless explicitly asked to implement.

## Tech Stack

### Backend (Go)

- **Language**: Go 1.26
- **HTTP framework**: Gin (`github.com/gin-gonic/gin`)
- **ORM**: GORM (`gorm.io/gorm`) with the PostgreSQL driver (`gorm.io/driver/postgres`)
- **Database**: PostgreSQL
- **Migrations**: GORM `AutoMigrate` driven by the model structs, run via the `apps/migration` command (no raw SQL)
- **Auth**: JWT (`github.com/golang-jwt/jwt/v5`) + bcrypt (`golang.org/x/crypto/bcrypt`) for password hashing
- **Validation**: Gin's binding via go-playground/validator (`binding:"..."` struct tags)
- **Money**: `github.com/shopspring/decimal` (never `float64` for amounts)
- **IDs**: `github.com/google/uuid`
- **Config**: environment variables, optionally loaded from `.env` in local dev (`github.com/joho/godotenv`)
- **Testing**: standard `testing` + `net/http/httptest`, plus a test database

### Frontend (web/)

- **Language**: TypeScript
- **Framework**: TBD — evaluating React (Next.js), Angular, or Vue.js (Nuxt). Decision pending.
- **Considerations**: Angular maps closest to the C#/OOP mindset (built-in DI, services, opinionated structure). React/Next.js has the larger ecosystem. Vue/Nuxt is the middle ground.

## Architecture

Layered architecture, consistent with the developer's Go/C# background:

```
Handlers (Gin) → Services → Repositories → Database
        ↕              ↕
     DTOs          Models (Entities)
```

- **Models**: GORM structs representing database tables. Live in the shared module.
- **DTOs**: Request/response structs with `json` and `binding` tags. Live per-consumer (the API owns its DTOs).
- **Repositories**: Data access layer. Encapsulate all database queries. One repository per aggregate root. Defined and implemented in the shared module so both the API and the worker reuse them.
- **Services**: Business logic. Orchestrate repositories, enforce rules, perform calculations. Owned by each consuming app.
- **Handlers**: HTTP layer (Gin). Parse/bind requests, call services, write the response envelope. No business logic.
- **Dependency wiring**: Plain constructor injection (`NewXxx(db)`, `NewService(repo)`), wired together in each app's `main`. No DI framework.

## Project Structure

A **multi-module Go workspace** (`go.work`) at the repo root. Each module has its own `go.mod` and dependency set; the workspace resolves cross-module imports locally without `replace` directives. The shared data layer lives under `internal/` so it is importable by every sibling module in this repo but by nothing outside it (Go's `internal/` visibility rule).

```
finance-tracker/
├── go.work                         # workspace: api, internal/shared, apps/migration, apps/worker
├── README.md
├── CLAUDE.md
├── .gitignore
│
├── api/                            # HTTP API application
│   ├── go.mod                      # module github.com/akhakpouri/finance-tracker/api
│   ├── .env.example                # committed template of required env vars
│   ├── cmd/
│   │   └── api/
│   │       └── main.go             # entrypoint: load config, open DB, build router, serve
│   └── internal/
│       ├── config/                 # API env binding (HTTP port, JWT secret, API prefix)
│       ├── dto/                    # request/response structs (Create/Update/Response)
│       ├── service/                # business logic, orchestrates shared repositories
│       ├── handler/                # Gin handlers + route registration
│       ├── middleware/             # auth, logging, recovery/error envelope
│       └── common/                 # response envelope + AppError types (HTTP concerns)
│
├── internal/
│   └── shared/                     # shared data layer — API + worker + migration tool
│       ├── go.mod                  # module github.com/akhakpouri/finance-tracker/internal/shared
│       ├── config/                 # shared (DB-only) config, e.g. DATABASE_URL
│       ├── database/               # GORM connection constructor + pool settings
│       ├── models/                 # GORM entities: user, account, transaction, category, budget (source of truth for the schema)
│       └── repository/             # repository interfaces + GORM implementations
│
├── apps/                           # standalone backend commands (own modules)
│   ├── migration/                  # module github.com/akhakpouri/finance-tracker/apps/migration — runs GORM AutoMigrate over the shared models
│   └── worker/                     # module github.com/akhakpouri/finance-tracker/apps/worker — background worker (future)
│
├── web/                            # TypeScript frontend (framework TBD)
│
└── docs/                           # shared documentation + project memory (docs/project-notes/)
```

### Structure Decisions

- **Multi-module workspace, not a single module.** The data layer is a separate module so the future background worker can depend on it without pulling in the API's HTTP/web dependencies, and vice versa. `go.work` ties the modules together for local development.
- **Shared data layer under `internal/`.** Because internal's parent is the repo root, every sibling module (`api`, `apps/migration`, `apps/worker`) can import `internal/shared/...`, but no external repository can. The privacy of the data layer is enforced by the compiler, for free.
- **`internal/shared` stays framework-agnostic.** No Gin, no HTTP types, no API DTOs. It must import cleanly into a worker that has no web server. If something web-shaped is tempting to add there, it belongs in `api/` instead.
- **Connection behavior in `shared`, connection config per-app.** `internal/shared/database` exposes a constructor (DSN in, `*gorm.DB` out) with the pool settings baked in, so every app opens connections identically. Each app loads its own DSN/config from its own environment and passes it in.
- **Repositories take a `*gorm.DB` via constructor injection.** No package-level/global DB. This lets the API and the worker each wire their own connection into the same repositories, and keeps multi-step writes wrappable in a single `db.Transaction(...)` by the caller.
- **Models are the schema source of truth.** Migrations are GORM `AutoMigrate` over the structs in `internal/shared/models` — no raw `.sql`, no separate schema definition to keep in sync. The `apps/migration` command is the single owner that runs it; the API and worker do **not** auto-migrate on boot, so they never race. Known limitation: `AutoMigrate` is additive-only (no drops/renames/destructive type changes, no rollback, no data backfills); a non-additive change will need a deliberate one-off and a revisit of this approach (see ADR-011).
- **DTOs are per-consumer.** The API owns its request/response shapes in `api/internal/dto`. Models (persistence) and DTOs (wire contract) stay strictly separate even when they look alike.
- **`common` over `utils` for cross-cutting plumbing.** The API's response-envelope and error types live in `api/internal/common`, named to signal "shared plumbing" and discourage a junk drawer. The top-level `apps/` directory holds deployable commands (`migration`, `worker`) — named for what they are (applications), not "utils".
- **Canonical module paths.** All modules are declared as `github.com/akhakpouri/finance-tracker/...`, matching the GitHub remote so `go get`/`go install` resolve correctly. Locally, `go.work` short-circuits resolution to the on-disk directories regardless.
- **`web/` structure is deferred** until a frontend framework is chosen.

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

- **UUIDs over auto-increment integers** for primary keys. Safer for a multi-client API — IDs are unpredictable and can be generated client-side if needed. Generate them in a GORM `BeforeCreate` hook on a shared embedded `Base` struct to stay DB-agnostic.
- **`account_type`, `transaction_type`, `category_type`, `period`** are modeled as Go named string types with `const` values (e.g. `type AccountType string`), stored as `varchar`. Application-level validation guards the allowed set.
- **Categories have a nullable `user_id`** (`*uuid.UUID`). When nil, the category is a system default (groceries, rent, utilities). When populated, it's user-created. The `is_system` flag makes querying easier without checking for null.
- **Transfers are modeled as transactions**, not a separate entity. A transfer creates two transaction records (one expense from the source, one income to the destination) in a single DB transaction. Consider adding a `transfer_id` field later to explicitly link the pair.
- **Budgets tie a user to a category with a spending limit.** The service layer calculates "amount spent in current period" by querying transactions against that category within the window derived from `start_date` + `period`.
- **`balance` on Account is a denormalized field.** Updated by the service layer on transaction create/update/delete. Source of truth is the sum of transactions; the cached balance avoids expensive aggregation on every read.
- **`decimal` for monetary amounts.** Never `float64`. Use `shopspring/decimal.Decimal` in Go with a GORM column type of `numeric(12,2)`.

## Phased Roadmap

### Phase 1 — Foundation
- Multi-module workspace and folder layout (`go.work`, `api`, `internal/shared`, `utils/*`)
- Database connection (GORM + PostgreSQL) in `internal/shared/database`
- `apps/migration` command running GORM `AutoMigrate` over the shared models
- Config management (env-based) — shared DB config + API config
- User entity wired end-to-end (model → repository → service → DTO → handler)
- Health check endpoint
- Error-handling middleware + response envelope

### Phase 2 — Authentication & Authorization
- User registration and login endpoints
- JWT token issuance and validation
- Password hashing (bcrypt)
- Auth middleware that resolves the current user and protects routes
- All subsequent routes require authentication

### Phase 3 — Core Domain
- Accounts CRUD (scoped to authenticated user)
- Categories CRUD (system defaults + user-created)
- Transactions CRUD with filtering (date range, category, account, amount)
- Pagination on list endpoints
- Request validation via binding tags + custom validators (positive amounts, valid dates)

### Phase 4 — Business Logic
- Budget system: set limits per category, calculate spending vs. limits
- Dashboard/summary endpoint: account balances, monthly spending by category, budget status
- Account-to-account transfers (atomic, wrapped in a single `db.Transaction`)

### Phase 5 — API Maturity
- Reusable offset (and later cursor) pagination
- Composable sorting and filtering via query parameters
- Structured logging
- Consistent API response envelope (success/error shape)
- Integration tests with `httptest` and a test database
- OpenAPI/Swagger docs (e.g. swaggo) with examples and tags

### Phase 6 — Background Worker
- Stand up `apps/worker` against the shared data layer
- Recurring/scheduled transaction processing
- Move long-running/derived work (e.g. balance recomputation, budget rollups) off the request path

### Phase 7 — Frontend Application
- Choose TypeScript framework (React/Next.js, Angular, or Vue/Nuxt)
- Scaffold `web/` with framework conventions
- Auth flow: login/register pages, JWT token storage, protected routes
- Core UI: accounts list, transaction list with filters, add/edit forms
- Dashboard: balances overview, spending by category, budget progress
- Typed API client consuming the Go backend

### Phase 8 — Stretch Goals
- CSV import/export
- Rate limiting
- Redis caching
- Additional async jobs on the worker

## Coding Conventions

- **Idiomatic Go.** `gofmt`/`goimports` clean, exported identifiers documented, short receiver names, packages named for what they provide.
- **Errors are values.** Wrap with `fmt.Errorf("...: %w", err)`, check with `errors.Is`/`errors.As`. Repositories translate `gorm.ErrRecordNotFound` into a domain error; services map domain errors to `AppError` (status + code) for the envelope.
- **`context.Context` first.** Every repository and service method takes `ctx context.Context` as its first parameter and threads it into GORM via `db.WithContext(ctx)`.
- **Constructor injection, no globals.** Wire dependencies explicitly in `main`. No package-level DB or singletons.
- **One file per concern.** One repository, model, or handler group per file. Keep it modular.
- **DTOs are not models.** Keep request/response structs separate from GORM entities, even when they look alike. Map at the boundary.
- **No business logic in handlers.** Handlers bind and delegate. Services decide. Repositories fetch.
- **`shared` imports nothing app-specific.** No Gin/HTTP in the data layer.
- **Schema changes go through the models + `apps/migration`.** Edit the GORM structs in `internal/shared/models`, then run `apps/migration` (`AutoMigrate`). No manual `ALTER` in the database. For a change `AutoMigrate` can't express, treat it as a deliberate exception and revisit ADR-011.

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

## Key Go / Gin / GORM Concepts in Play

- **`go.work` multi-module workspaces** — cross-module local development without `replace` directives.
- **Go's `internal/` visibility rule** — how it scopes the shared data layer to this repo.
- **GORM**: model tags, `BeforeCreate` hooks, relationships and preloading, `db.WithContext`, and `db.Transaction` for atomic multi-step writes.
- **Gin**: route groups, `ShouldBindJSON` + binding validation, middleware chains, and `c.JSON` for the envelope.
- **Producer- vs consumer-defined interfaces** — starting producer-side in `shared`, with room to move toward consumer-defined interfaces later.
- **`shopspring/decimal`** semantics for money math (no float rounding).

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
