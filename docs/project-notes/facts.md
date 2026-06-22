# Project Facts

Key configuration values, constants, and reference info. Check here before assuming defaults.

> Note: the project pivoted from Python/FastAPI to Go on 2026-06-22. See ADR-007.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Go 1.26 |
| HTTP framework | Gin (`github.com/gin-gonic/gin`) |
| ORM | GORM (`gorm.io/gorm`) + PostgreSQL driver (`gorm.io/driver/postgres`) |
| Database | PostgreSQL |
| Migrations | GORM `AutoMigrate` over the model structs, run via `apps/migration` (no raw SQL) |
| Auth | JWT (`github.com/golang-jwt/jwt/v5`) + bcrypt (`golang.org/x/crypto/bcrypt`) |
| Validation | Gin binding / go-playground/validator (`binding:"..."` tags) |
| Money | `github.com/shopspring/decimal` |
| IDs | `github.com/google/uuid` |
| Config | env vars + optional `.env` (`github.com/joho/godotenv`) |
| Testing | stdlib `testing` + `net/http/httptest` + test database |
| Frontend | TypeScript, framework TBD |

## Modules (go.work)

| Module path | Directory | Role |
|-------------|-----------|------|
| `github.com/akhakpouri/finance-tracker/api` | `api/` | HTTP API application |
| `github.com/akhakpouri/finance-tracker/internal/shared` | `internal/shared/` | Shared data layer (models, repositories, DB connection) |
| `github.com/akhakpouri/finance-tracker/apps/migration` | `apps/migration/` | Runs GORM AutoMigrate over the shared models |
| `github.com/akhakpouri/finance-tracker/apps/worker` | `apps/worker/` | Background worker (future) |

## Conventions

- Idiomatic Go: `gofmt`/`goimports` clean, exported identifiers documented
- Errors are values: wrap with `%w`, inspect with `errors.Is`/`errors.As`
- `context.Context` is the first parameter of every repository and service method; thread it via `db.WithContext(ctx)`
- Constructor injection, no package-level/global DB or singletons
- One file per concern
- DTOs (request/response structs) strictly separated from Models (GORM entities)
- `internal/shared` imports nothing app-specific (no Gin/HTTP)
- Every schema change is made on the GORM model structs and applied by running `apps/migration` (`AutoMigrate`) — no manual SQL/`ALTER`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `postgres://user:pass@localhost:5432/finance?sslmode=disable` |
| JWT_SECRET | JWT signing key | (generate a secure random value) |
| PORT | API HTTP port | `8080` |
| API_PREFIX | API route prefix | `/api/v1` |
| DEBUG | Verbose SQL/logging | `true` / `false` |

## Domain Enums (Go named string types)

- **AccountType:** checking, savings, credit_card, cash
- **TransactionType:** income, expense, transfer
- **CategoryType:** income, expense
- **BudgetPeriod:** monthly, weekly
