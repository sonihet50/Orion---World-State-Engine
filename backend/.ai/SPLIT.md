# Work Split: File Ownership & Frozen Files

> **NOTICE FOR AI AGENTS**: Three people work in parallel on separate branches after the `step0` tag. Before editing
> any file, find it below. If your branch does not own it, or it is frozen, **stop and ask** instead of editing it.
> Source: *Orion: Task Split for Manual Features and Extraction* (Oct 10, 2026).

Paths are repo-relative. `routes/` means `backend/app/api/v1/routes/`. Files marked *(new)* do not exist until the
owner, or Step 0, creates them.

---

## 1. Branches

All feature branches start from the `step0` tag and follow `feature/<slug>`. Nobody commits to `main`.

| Owner | Branch | Scope |
| --- | --- | --- |
| Step 0 (one person/session) | `feature/step0-scaffold` | Baseline, rules, router stubs, the one planned migration, API contracts, seed script. Merged to `main` and tagged `step0` before anyone else branches. |
| Person A | `feature/manual-entities` | Entities, facts, merge, aliases, contradiction choice |
| Person B | `feature/graph-timeline` | Relationships, events/timeline, time-slice graph |
| Extraction | `feature/extraction-review` | Event offsets, propose-then-apply re-extraction, review modal, demo manuscript |

---

## 2. File Ownership

### Person A: entities, facts, contradictions

| Layer | Files |
| --- | --- |
| Routes | `routes/entities.py`, `routes/contradictions.py` |
| Schemas | `backend/app/schemas/entity.py` |
| Services | `backend/app/services/entity_service.py`, `backend/app/services/merge_service.py` *(new)* |
| Tests | `backend/app/tests/test_manual_entities.py` *(new)* |
| Frontend | `Frontend/src/store/useWorldStore.ts`, `Frontend/src/pages/EntityLedger.tsx`, `Frontend/src/components/EntityPanel.tsx`, `Frontend/src/pages/Contradictions.tsx`, `Frontend/src/data/mockData.ts`, `Frontend/src/api/entities.ts` *(stub from Step 0)* |

### Person B: relationships, timeline, time-slice graph

| Layer | Files |
| --- | --- |
| Routes | `routes/relationships.py` *(stub from Step 0)*, `routes/events.py` *(stub from Step 0)*, `routes/graph.py` |
| Schemas | `backend/app/schemas/relationship.py` *(new)*, `backend/app/schemas/timeline.py`, `backend/app/schemas/graph.py` |
| Services | `backend/app/services/timeline_service.py`, `backend/app/services/graph_service.py` |
| Frontend | `Frontend/src/pages/WorldGraph.tsx`, `Frontend/src/pages/WorldTimeline.tsx`, `Frontend/src/api/relationships.ts` *(stub from Step 0)*, `Frontend/src/api/events.ts` *(stub from Step 0)* |

### Extraction person: re-extraction review

The source doc gives no explicit list for this role. These are the files its conflict rules keep Person A and
Person B away from, plus the files its tasks name.

| Layer | Files |
| --- | --- |
| Routes | `routes/chapters.py`, `routes/proposals.py` *(stub from Step 0)* |
| Services | `backend/app/services/world_state_service.py`, `backend/app/services/chapter_service.py` |
| Pipeline / workers | `backend/app/pipeline/`, `backend/app/workers/` |
| Frontend | `Frontend/src/pages/WritingRoom.tsx`, `Frontend/src/pages/ProcessingWorld.tsx`, `Frontend/src/api/proposals.ts` *(stub from Step 0)* |
| Fixture | The demo manuscript, once frozen (3–5 short chapter headings) |

### Shared API stubs

Step 0 creates typed stubs in `Frontend/src/api/`, and each owner fills in only their own file: `entities.ts` (A),
`relationships.ts` and `events.ts` (B), `proposals.ts` (Extraction). The source doc also gives Person B
`src/api/*`. Read that as the B-owned files above, not the other owners' stubs.

---

## 3. Frozen Files (no edits after the `step0` tag)

| File / path | Why |
| --- | --- |
| `backend/app/api/v1/router.py` | Step 0 registers every router up front |
| `Frontend/src/App.tsx` | Shared routing for every page |
| `backend/app/tests/conftest.py` | Shared fixtures for every branch |
| `docs/api.md` | The contract every branch builds against |
| `Frontend/src/api/stub.ts` | Shared `notImplemented()` placeholder used by every Step 0 client stub |
| `backend/app/models/` | Schema frozen at `step0` (see Rule S.1) |
| `backend/alembic/versions/` | Schema frozen at `step0` (see Rule S.1) |

---

## 4. Don't-Touch Lists

- **Person A and Person B never touch:** `backend/app/services/world_state_service.py`, `backend/app/pipeline/`,
  `backend/app/workers/`, `routes/chapters.py`, `backend/app/services/chapter_service.py`,
  `Frontend/src/pages/WritingRoom.tsx`, `Frontend/src/pages/ProcessingWorld.tsx`.
- **The extraction person never touches:** `routes/entities.py`, `routes/relationships.py`, `routes/events.py`, or
  Person A's and Person B's pages (`EntityLedger.tsx`, `EntityPanel.tsx`, `Contradictions.tsx`, `WorldGraph.tsx`,
  `WorldTimeline.tsx`).
- **Nobody edits** the frozen files in section 3.

---

## 5. Shared-Code Rules

- **Repositories are append-only.** In `backend/app/repositories/`, add new methods; never change or remove existing
  ones, because another branch may depend on them.
- **New TypeScript types go in new files.** Don't add to a shared types file.
- **Person A's merge writes through the models directly**, not through Person B's repository methods.
- **Apply goes through the manual endpoints.** The extraction review modal calls Person A's and Person B's
  endpoints, so every accepted change goes through one write path as a new version (see RULES.md Rule 3.4).

---

## 6. Schema Rule

- **Rule S.1: No model or migration changes on feature branches.** Don't edit `backend/app/models/` or add files
  under `backend/alembic/versions/` on any `feature/*` branch other than `feature/step0-scaffold`.
  - **Why:** the repo has exactly one Alembic head (`ef5362e51e02`, which revises `1fa5cd397cfc`). Two branches that each
    add a migration with the same `down_revision` create two heads, and `alembic upgrade head` then fails until
    someone writes a merge migration.
  - **The one exception:** Step 0 added the single planned migration, `ef5362e51e02` (`events.sequence_index`,
    nullable int). After the `step0` tag, the schema is frozen for everyone. `app/tests/test_migrations.py` fails
    if a second head appears.
  - **If a feature needs a schema change:** stop and raise it with the team. Don't work around it with the
    `database-migration` skill. The proposals flow stores its data as a JSON file keyed by job id for this reason.
