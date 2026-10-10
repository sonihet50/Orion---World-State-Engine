# Non-Negotiable Rules & Invariants

> **NOTICE FOR AI AGENTS**: These rules are binding constraints derived from the Software Requirements Specification ([`docs/srs.md`](../../docs/srs.md)), architectural safety requirements, and production reliability standards. Never bypass or disable these checks.

---

## 1. Multi-Tenant Isolation (SRS REQ-4 & Section 5.3)

- **Rule 1.1**: Every project ("World") must be scoped to an authenticated user (`user_id`).
- **Rule 1.2**: Never execute a database query or mutation that accesses world data without verifying ownership against the authenticated `current_user.id`.
- **Rule 1.3**: When running tests or public endpoints, handle optional users explicitly; never leak tenant identifiers across sessions.

---

## 2. Rule-Based Contradiction Verification (SRS REQ-27)

- **Rule 2.1**: **NEVER delegate contradiction detection to a Language Model.**
- **Rule 2.2**: Contradiction detection must be executed via deterministic Python algorithms in [`ConsistencyService`](../app/services/consistency_service.py) or dedicated rule modules (today: `app/consistency/`).
- **Rule 2.3**: Contradiction rule categories and their status (details: [`context/consistency_engine.md`](context/consistency_engine.md)):
  1. **Age Monotonicity (REQ-23)** — IMPLEMENTED (`AGE_MONOTONIC`). No flashback marker exists in the data model, so flashbacks can be flagged.
  2. **Location Clash (REQ-24)** — DEFERRED: the frozen schema has no event location/time, so "same time, two places" cannot be decided.
  3. **Relationship Incompatibility (REQ-25)** — IMPLEMENTED for the explicit pairs in `consistency/vocabulary.py` and for a changing `FATHER_OF`; other parentage predicates are not covered.
  4. **Post-Mortem Actions (REQ-26)** — PARTIAL: a later `status` of alive after dead is flagged (`DEAD_THEN_ALIVE`); speaking/acting after death is DEFERRED (no speaker attribution, no participant roles).
  5. **Temporal Graph Cycles** — IMPLEMENTED (`TEMPORAL_CYCLE`), within one chapter's relations only (temporal relations are not persisted).
  Rules act only on the controlled vocabulary; unknown properties/predicates never create contradictions.

---

## 3. Permanent State Immutability (SRS REQ-22 & Section 6)

- **Rule 3.1**: **Never execute an in-place SQL `UPDATE` on fact values or relationship types.**
- **Rule 3.2**: When an attribute or relationship is modified, append a new version row (`FactVersion`, `RelationshipVersion`) with the appropriate status:
  - `ACTIVE`: The current confirmed value.
  - `SUPERSEDED`: A valid chronological evolution or change of state.
  - `CONTRADICTED`: A conflicting value that triggered a contradiction record.
- **Rule 3.3**: Never delete historical chapters or versions when re-extracting text.
- **Rule 3.4 — Manual operations carve-out**: Rules 3.1–3.3 were written for the extraction pipeline and every other automated write path. Operations the author starts explicitly through the API follow these rules instead:
  - **Manual edits still append new versions.** Editing a fact value or relationship type through the API appends a new `FactVersion` / `RelationshipVersion` and supersedes the previous one, exactly as Rule 3.2 says. It never updates the existing row in place.
  - **Merge may repoint foreign keys and change version status, but never rewrites a value or a type.** Merging entity B into entity A may move B's facts, relationships, mentions, aliases and event participations to A, and may change version status (for example `ACTIVE` → `SUPERSEDED`) to resolve duplicates. It must never change a stored `value` or relationship type.
  - **Author-initiated deletes of entities, relationships, events and facts are allowed.** REQ-22 forbids the *system* from overwriting stored facts. It does not forbid the author from deliberately removing something. Deletes must still verify ownership (Rule 1.2), and the pipeline must never issue them on its own.

---

## 4. Performance Latency Budgets (SRS Section 5.1)

- **Rule 4.1**: Single chapter extraction must complete in **≤ 10 seconds**.
- **Rule 4.2**: Contradiction detection must complete in **≤ 5 seconds**.
- **Rule 4.3**: Character chat responses must be returned in **≤ 3 seconds**.

---

## 5. Database Schema & Migration Invariants

- **Rule 5.1**: Every change to SQLAlchemy models in [`app/models/`](../app/models/) **must** include an Alembic migration in [`alembic/versions/`](../alembic/versions/).
- **Rule 5.2**: All foreign keys must define explicit cascading semantics (`ondelete="CASCADE"` or `ondelete="SET NULL"`).
- **Rule 5.3**: Avoid naming column attributes with reserved SQLAlchemy names (e.g. always import `from sqlalchemy.orm import relationship as sa_relationship` if a model class defines a column named `relationship`).

---

## 6. API & Schema Standards

- **Rule 6.1**: All Pydantic models must use Pydantic V2 `model_config = ConfigDict(from_attributes=True)`. Do not use deprecated `class Config: from_attributes = True`.
- **Rule 6.2**: All datetime objects must use timezone-aware standards: `datetime.now(timezone.utc)` instead of `datetime.utcnow()`.
- **Rule 6.3**: HTTP status codes must adhere to REST conventions:
  - Resource created: `201 Created`
  - Asynchronous extraction queued: `202 Accepted`
  - Deletion succeeded: `204 No Content`
  - Missing resource: `404 Not Found`
  - Unauthorized: `401 Unauthorized`

---

## 7. Testing & Verification Gate

- **Rule 7.1**: An agent may **not** declare a task complete if any test in [`app/tests/`](../app/tests/) fails.
- **Rule 7.2**: All new services, endpoints, or rules must be accompanied by unit or integration tests.
- **Rule 7.3**: SQLite in-memory test fixtures must use `StaticPool` and `check_same_thread=False` to prevent thread-isolation `OperationalError` table misses.
