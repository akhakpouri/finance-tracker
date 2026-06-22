# Work Log

Tracking active and completed work with GitHub issue references.

> **2026-06-22:** Pivoted from Python/FastAPI to Go (ADR-007). Summaries below are restated in Go terms; existing GitHub issue numbers are reused. Phase 6 is now the background worker and the frontend moved to Phase 7 (see CLAUDE.md roadmap).

## Active

| Issue | Phase | Summary | Status |
|-------|-------|---------|--------|
| #3 | Phase 1 | Project structure and multi-module workspace layout | Open |
| #4 | Phase 1 | Database connection (GORM + PostgreSQL) in `internal/shared` | Open |
| #5 | Phase 1 | `apps/migration` command running GORM AutoMigrate over the shared models | Open |
| #6 | Phase 1 | Config management (env-based: shared DB config + API config) | Open |
| #7 | Phase 1 | User entity end-to-end (model → repo → service → DTO → handler) | Open |
| #8 | Phase 1 | Health check endpoint | Open |
| #9 | Phase 1 | Error-handling middleware + response envelope | Open |

## Upcoming

| Issue | Phase | Summary |
|-------|-------|---------|
| #10 | Phase 2 | User registration and login |
| #11 | Phase 2 | JWT token issuance and validation |
| #12 | Phase 2 | Auth middleware (resolve current user, protect routes) |
| #13 | Phase 3 | Accounts CRUD |
| #14 | Phase 3 | Categories CRUD |
| #15 | Phase 3 | Transactions CRUD with filtering |
| #16 | Phase 3 | Pagination on list endpoints |
| #17 | Phase 3 | Request validation (binding tags + custom validators) |
| #18 | Phase 4 | Budget system |
| #19 | Phase 4 | Dashboard/summary endpoint |
| #20 | Phase 4 | Account-to-account transfers |
| #21-#25 | Phase 5 | API maturity (pagination, sorting, logging, tests, OpenAPI) |
| #26-#29 | Phase 6 | Background worker (recurring transactions, off-request jobs) |
| #30-#34 | Phase 7 | Frontend application |
| #35+ | Phase 8 | Stretch goals (CSV, rate limiting, caching) |

## Completed

| Issue | Phase | Summary | Date |
|-------|-------|---------|------|
