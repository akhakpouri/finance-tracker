# Finance Tracker

A personal finance tracker: track accounts, categorize income and expenses, set budgets, and see where your money goes. Built as a **multi-module Go monorepo** with a Gin + GORM + PostgreSQL backend and a TypeScript frontend (framework TBD).

> Status: early development (Phase 1 — foundation). Structure and APIs are still settling.

## Why this project

A real-depth application — shared data layer, an HTTP API, and an eventual background worker — built to practice idiomatic Go with clean module boundaries, the repository/service/handler pattern, and PostgreSQL.

## Tech Stack

| Layer | Technology |
|------|-----------|
| Language | Go 1.26 |
| HTTP | Gin |
| ORM | GORM (PostgreSQL driver) |
| Database | PostgreSQL |
| Migrations | GORM AutoMigrate (via `apps/migration`) |
| Auth | JWT + bcrypt |
| Money | shopspring/decimal |
| IDs | google/uuid |
| Frontend | TypeScript (framework TBD) |

## Repository Layout

A `go.work` workspace ties several modules together. The data layer is a shared module so both the API and a future background worker can reuse the same models and repositories.

```
finance-tracker/
├── go.work              # workspace stitching the modules together
├── api/                 # HTTP API application (Gin)
├── internal/
│   └── shared/          # shared data layer: models, repositories, DB connection (imported by every app)
├── apps/
│   ├── migration/       # runs GORM AutoMigrate over the shared models
│   └── worker/          # background worker (future)
├── web/                 # TypeScript frontend (TBD)
└── docs/                # documentation + project notes
```

The shared data layer sits under `internal/` so it's importable by every module in this repo but by nothing outside it (Go's `internal/` visibility rule). See [`CLAUDE.md`](./CLAUDE.md) for the full architecture and the domain model.

## Getting Started

> Prerequisites: Go 1.26+ and PostgreSQL.

```bash
# Clone
git clone https://github.com/akhakpouri/finance-tracker.git
cd finance-tracker

# Sync the workspace
go work sync

# Configure the API (copy and edit the example env)
cp api/.env.example api/.env

# Run database migrations (GORM AutoMigrate over the shared models)
# go run ./apps/migration

# Run the API
# go run ./api/cmd/api
```

Commands marked with `#` are the intended workflow and will be wired up as Phase 1 lands.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/finance?sslmode=disable` |
| `JWT_SECRET` | JWT signing key | (generate a secure random value) |
| `PORT` | API HTTP port | `8080` |
| `API_PREFIX` | API route prefix | `/api/v1` |
| `DEBUG` | Verbose SQL/logging | `true` / `false` |

## Roadmap

1. **Foundation** — workspace, DB connection, migrations, config, User end-to-end, health check
2. **Auth** — registration, login, JWT, password hashing, route protection
3. **Core domain** — accounts, categories, transactions (with filtering + pagination)
4. **Business logic** — budgets, dashboard/summary, atomic transfers
5. **API maturity** — pagination/sorting patterns, logging, tests, OpenAPI
6. **Background worker** — recurring transactions, off-request-path jobs
7. **Frontend** — TypeScript app consuming the API
8. **Stretch** — CSV import/export, rate limiting, caching

See [`CLAUDE.md`](./CLAUDE.md) for full detail and [`docs/project-notes/`](./docs/project-notes/) for decisions, facts, and the work log.

## License

See [LICENSE](./LICENSE).
