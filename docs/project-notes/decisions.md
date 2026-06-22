# Architectural Decisions

Record of significant technical choices and their rationale. Check here before proposing changes.

---

## ADR-001: Monorepo with sibling directories

**Date:** 2026-04-15
**Status:** Superseded by ADR-008

**Context:** Need to organize a full-stack app with a Python backend and TypeScript frontend.

**Decision:** Use a monorepo with `api/` and `web/` as sibling directories at the repo root. Each is independently buildable and deployable.

**Rationale:** Avoids nesting one app inside the other, which creates deployment and build-tool headaches. Shared docs and config live at the root.

**Update (2026-06-22):** Still a monorepo, but now a multi-module Go workspace with more than two members. See ADR-008.

---

## ADR-002: Layered architecture (Router > Service > Repository)

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Developer has strong Go/C# background with repository pattern and layered architecture experience.

**Decision:** Follow Handlers > Services > Repositories > Database pattern. No business logic in handlers. Repositories encapsulate all DB queries.

**Rationale:** Maps familiar patterns into the chosen ecosystem. Layering is preserved across the Go pivot (ADR-007); see ADR-010 for repository-interface placement.

---

## ADR-003: UUIDs for primary keys

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Choosing between auto-increment integers and UUIDs for entity IDs.

**Decision:** Use UUIDs for all primary keys.

**Rationale:** Safer for a multi-client API. IDs are unpredictable and can be generated client-side if needed.

---

## ADR-004: Decimal for monetary amounts

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Need to store financial amounts accurately.

**Decision:** Use a fixed-precision decimal type with `numeric(12,2)` columns. Never use float for money.

**Rationale:** Floating point arithmetic introduces rounding errors that are unacceptable in financial applications.

**Update (2026-06-22):** In Go this means `github.com/shopspring/decimal` with a GORM `type:numeric(12,2)` column tag. See ADR-007.

---

## ADR-005: Denormalized balance on Account

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Account balance can be derived from summing transactions but that's expensive on every read.

**Decision:** Store `balance` as a denormalized field on Account, updated by the service layer on transaction create/update/delete.

**Rationale:** Avoids expensive aggregation on every read. Source of truth is the sum of transactions; the cached balance is a performance optimization.

---

## ADR-006: Transfers modeled as paired transactions

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Need to support transfers between accounts.

**Decision:** A transfer creates two transaction records (one expense from source, one income to destination) in a single DB transaction. Consider adding a `transfer_id` field later.

**Rationale:** Keeps the transaction model simple. No separate transfer entity needed.

---

## ADR-007: Pivot backend from Python/FastAPI to Go

**Date:** 2026-06-22
**Status:** Accepted

**Context:** The backend was originally scaffolded in Python/FastAPI as a first-Python learning exercise. The developer decided to stay on the Go path they are most interested in and most productive with. The Python `api/` was deleted before any meaningful logic was written.

**Decision:** Rebuild the backend in Go. Stack: Gin (HTTP), GORM + PostgreSQL driver (ORM), GORM `AutoMigrate` for migrations (see ADR-011), JWT + bcrypt (auth), Gin binding/validator (validation), `shopspring/decimal` (money), `google/uuid` (IDs), env-based config.

**Rationale:** Go is the developer's primary language and the intended long-term direction. The domain model, layered architecture, UUID/decimal/denormalized-balance/transfer decisions (ADR-002–006) all carry over unchanged; only the language and framework-specific idioms change.

**Consequences:** Python-specific docs and code are obsolete (see bugs.md note). FastAPI `Depends()` DI is replaced by plain constructor injection. Async-by-default no longer applies (Go handles concurrency differently).

---

## ADR-008: Multi-module Go workspace monorepo

**Date:** 2026-06-22
**Status:** Accepted

**Context:** A background worker is planned that must share the data layer (models, repositories) with the HTTP API. A single-module layout would force the API and worker to share one dependency set.

**Decision:** Use a `go.work` workspace with separate modules: `api/` (HTTP API), `internal/shared/` (shared data layer), `apps/migration/` (migration runner), `apps/worker/` (future worker). `go.work` resolves cross-module imports locally without `replace` directives.

**Rationale:** Each app keeps an isolated dependency set — the worker won't pull Gin/HTTP deps, the API won't pull worker-only deps. The shared data layer is built and tested once and reused by every consumer.

**Consequences:** More `go.mod` files to maintain and upgrade. `go.work` is committed so the workspace is reproducible for any clone.

---

## ADR-009: Shared data layer under `internal/`

**Date:** 2026-06-22
**Status:** Accepted

**Context:** The shared data-layer module should be reusable by every app in this repo but not by external repositories.

**Decision:** Place the shared module at `internal/shared/`. Because internal's parent is the repo root, every sibling module (`api`, `apps/migration`, `apps/worker`) can import `internal/shared/...`, while Go's `internal/` visibility rule blocks any external repo from importing it.

**Rationale:** Compiler-enforced privacy of the data layer at zero cost. The shared module stays framework-agnostic (no Gin/HTTP), connection *behavior* lives in `shared/database` while connection *config* stays per-app, and repositories use constructor-injected `*gorm.DB` (no globals).

**Resolved (2026-06-22):** (1) Module paths are canonical (`github.com/akhakpouri/finance-tracker/...`), matching the GitHub remote so `go get`/`go install` resolve correctly; the `go.work` workspace short-circuits to local directories for development. (2) The deployable-commands directory was renamed `utils/` → `apps/`, since `migration` and `worker` are applications, not utilities.

---

## ADR-010: Repository interfaces defined producer-side (for now)

**Date:** 2026-06-22
**Status:** Accepted

**Context:** With a separate data-layer module consumed by both the API and the worker, the repository interfaces can live either with their implementations (producer-side, in `shared`) or with each consumer (Go-idiomatic, consumer-side).

**Decision:** Start with producer-defined interfaces in `internal/shared/repository` — interface plus GORM implementation together. Both the API and the worker import the shared interface.

**Rationale:** Maps directly onto the developer's C#/repository-pattern mental model and gives both consumers a single shared contract to reuse. Revisit toward consumer-defined interfaces (each app declaring the narrow interface it needs) as Go comfort grows — consistent with the "start familiar, get more idiomatic over time" approach.

---

## ADR-011: GORM AutoMigrate for schema migrations

**Date:** 2026-06-22
**Status:** Accepted (supersedes the golang-migrate choice in ADR-007)

**Context:** ADR-007 initially listed golang-migrate with raw `.up.sql`/`.down.sql` files. With GORM already modeling the schema via struct tags, maintaining a parallel set of hand-written SQL files duplicates the source of truth.

**Decision:** Drop golang-migrate and raw SQL. The GORM model structs in `internal/shared/models` are the single source of truth for the schema. The `apps/migration` command runs `db.AutoMigrate(...)` over those models. It is the sole owner of migration execution — the API and worker do not auto-migrate on boot, so they never race.

**Rationale:** One source of truth (the structs), no struct/SQL drift, and the fastest path while the schema is still forming in Phases 1–3. Fits the developer's preference to lean on GORM.

**Consequences / known limitations:** `AutoMigrate` is **additive and one-directional** — it creates tables/columns/indexes but will not drop or rename columns, perform destructive type changes, roll back, or run data backfills, and it keeps no migration version history. The first non-additive change (rename, constraint change, backfill) will require a deliberate one-off and likely a revisit of this decision (candidates if revisited: `gormigrate` for versioned Go migrations with rollback, or golang-migrate). Accepted knowingly for early-phase speed.
