# Architectural Decisions

Record of significant technical choices and their rationale. Check here before proposing changes.

---

## ADR-001: Monorepo with sibling directories

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Need to organize a full-stack app with a Python backend and TypeScript frontend.

**Decision:** Use a monorepo with `api/` and `web/` as sibling directories at the repo root. Each is independently buildable and deployable.

**Rationale:** Avoids nesting one app inside the other, which creates deployment and build-tool headaches. Shared docs and config live at the root.

---

## ADR-002: Layered architecture (Router > Service > Repository)

**Date:** 2026-04-15
**Status:** Accepted

**Context:** Developer has strong Go/C# background with repository pattern and layered architecture experience.

**Decision:** Follow Routers (Handlers) > Services > Repositories > Database pattern. No business logic in routers. Repositories encapsulate all DB queries.

**Rationale:** Maps familiar patterns into the Python/FastAPI ecosystem. Start class-based, refactor toward more Pythonic approaches as comfort grows.

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

**Decision:** Use `Numeric(precision=12, scale=2)` in SQLAlchemy and `Decimal` in Pydantic schemas. Never use float for money.

**Rationale:** Floating point arithmetic introduces rounding errors that are unacceptable in financial applications.

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
