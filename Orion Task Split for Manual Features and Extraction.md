# Orion: Task Split for Manual Features and Extraction

Oct 10, 2026 · @Het Soni

## Correction: extraction is deterministic

Extraction runs at temperature 0, so re-running an unchanged chapter should give near-identical output. An earlier answer said 0.7; that value is in `llm_client.py`, which only the chat feature uses. Extraction goes through the separate `extractor/` package (NuExtract at temperature 0), so edit-triggered extraction is more viable than first assumed.

## Does "frozen state, ask the author" hold up?

Only half of it works today, so edit-triggered extraction must propose changes first and apply them only after the author accepts.

**Already in the code:** a conflicting claim is saved as CONTRADICTED, the old value stays ACTIVE, and `resolve` accepts a `preferred_*_version_id`, so the author picks the winner.

**Two leaks:**

1. When the rules call a change "valid evolution", the pipeline sets the old fact or relationship to SUPERSEDED on its own, with no author involved.
2. Re-extracting an edited chapter writes straight into the world tables, and old chapter-version rows are never removed. Every edit double-counts that chapter, which also breaks the time slider. A name the world hasn't seen becomes a duplicate entity.

**Propose, then apply:**

- On edit, the job runs the extractor only and diffs the result against the current world. It saves the proposals as a JSON file keyed by job id (`processing_jobs` has no column for it, and a schema change is off the table). The world tables are untouched.
- A review modal shows new items (tick to add), already-known items (hidden), and changed items (the author decides).
- Apply calls the same endpoints Person A and Person B build for manual edits, so every accepted change is a new version through one write path.
- The first upload stays direct-write. The world is empty, so there is nothing to protect.

## Two demo facts that change the tasks

- **Chapter headings drive the time slider.** Upload auto-detects chapter headings and otherwise creates one chapter. A 1–2 page manuscript without headings gives a slider with one stop. Time = chapter number, so the demo manuscript needs 3–5 short chapter headings. That is zero code, but someone has to own writing and freezing it.
- **Event offsets are dropped before the DB.** Extractor events carry a character offset (`e["start"]`), but it never reaches the database. Ordering inside a chapter falls back to insertion time. The fix is in the extraction person's section.

## Step 0: scaffold before anyone branches

One person (or one Claude Code session) works through these on `feature/step0-scaffold`, one commit per task, and merges to `main` before anyone branches. The repo workflow forbids committing to `main`, and its test rule blocks any agent from finishing while a test fails, so the baseline task comes first. The seed script is the longest task; the rest are short.

1. **Branch and baseline.** Create `feature/step0-scaffold`. Run the full backend test suite and the frontend build and lint, and record every failure that exists before any change. Fix each one or mark it xfail with a reason. Rule 7.1 in `.ai/RULES.md` stops an agent from finishing a task while any test fails, so unfixed failures block everyone's sessions.
2. **Amend `.ai/RULES.md` for manual operations.** Rules 3.1 and 3.3 were written for the extraction pipeline. Add a carve-out: manual edits still append new versions; merge may repoint foreign keys and change version status but never rewrites a value or a type; author-initiated deletes of entities, relationships, events and facts are allowed. Agree the wording with the team first, because the SRS cites REQ-22 for this rule.
3. **Add `.ai/SPLIT.md` and a root `CLAUDE.md`.** Only `backend/CLAUDE.md` exists today, so a session started at the repo root may never load it. `SPLIT.md` holds the ownership tables and frozen-file lists from this doc; the root `CLAUDE.md` points at `backend/CLAUDE.md` and `SPLIT.md`. Add one rule: no model or migration changes on feature branches. The repo has one Alembic head (`1fa5cd397cfc`), and two branches each adding a migration would create two.
4. **Scaffold the routers.** Create empty `routes/relationships.py`, `routes/events.py` and `routes/proposals.py`, and register all three in `router.py`.
5. **Add the migration.** Add `events.sequence_index` (nullable int) to the model with an Alembic migration, and as an optional field on `TimelineEventResponse`. Prove it with `upgrade head` on a fresh SQLite database (rule 5.1).
6. **Write the contracts.** Add sections to `docs/api.md` for merge, bulk-delete and aliases; relationship CRUD; event CRUD and reorder; `GET /graph?as_of_chapter=N`; and `GET /jobs/{id}/proposals`, using the status codes from rule 6.3. Create typed stub modules `src/api/entities.ts`, `relationships.ts`, `events.ts` and `proposals.ts`; each owner fills in their own file.
7. **Write the seed script.** `backend/scripts/seed_demo_world.py`, deterministic and idempotent, inserts a small world through the models with no extraction, so Person A and Person B don't depend on extraction quality. Contents: 3 chapters; about 6 entities with aliases, including a duplicate pair to merge; a fact that evolves across chapters; relationships with versions in different chapters, including a type change; events in several chapters, two in the same chapter; one unresolved and one resolved contradiction; mentions linked through extraction run, chapter version and chapter (Person B's node rule needs this). Add a test that runs it and checks the counts.
8. **Merge and tag.** Run the tests, merge to `main`, and tag `step0`. Everyone branches from the tag, using the repo's `feature/<slug>` pattern: `feature/manual-entities` (Person A), `feature/graph-timeline` (Person B) and `feature/extraction-review` (extraction).

## Person A: entities, facts, contradictions

Person A makes the existing edits persist, builds merge, and gives the author a real choice on each contradiction.

| Priority | Task | Detail |
| --- | --- | --- |
| P0 | Persistence | In `useWorldStore.ts`, `updateEntity`, `deleteEntity`, `addFact` and `deleteFact` only change local state. Wire them to the existing `PUT/DELETE /entities` and `POST/DELETE /entities/{id}/facts`. The add-fact form needs a `property_name` field. |
| P0 | Merge | `POST /entities/merge {source_id, target_id}` in a new `merge_service.py`, as one transaction (rules below). UI: pick two, choose the survivor, confirm. |
| P0 | Contradiction choice | Confirmed: `Contradictions.tsx` calls resolve with no `preferred_*_version_id`, so it only marks the item resolved and the author cannot pick a winner. Add "keep old" and "keep new" buttons that send `preferred_fact_version_id` or `preferred_relationship_version_id`. This is the "consult the author" mechanism. |
| P1 | Fact edits | Confirmed bug: `fact_repo.add_version` does not retire the previous ACTIVE version, so a manual fact edit leaves two ACTIVE values. Mark the previous ACTIVE version SUPERSEDED when adding a manual one. Call the consistency check from `add_fact`. |
| P1 | Aliases and retype | Add and remove aliases by string (don't change the `EntityResponse` shape), plus inline type editing. |
| P1 | Bulk delete | `POST /entities/bulk-delete`. Lower priority, because a 2-page manuscript yields a handful of entities. |
| P1 | Tests | `test_manual_entities.py`, one test per merge rule. |

**Merge rules (one transaction):**

- Move the source's name and aliases onto the target, deduplicated. This stops the review flow from re-proposing the merged-away name.
- Repoint mentions to the target.
- Fold facts with the same `property_name`. If both are ACTIVE with different values, keep the target's and mark the other SUPERSEDED.
- Drop duplicate event participants.
- Delete relationship self-loops. If repointing creates a pair the target already has, move the versions onto the existing row.
- Reject if the entities are in different worlds, source equals target, or a job is processing.

**Orphan contradictions:** deleting an entity cascades to its fact versions, but a contradiction only sets its links to null. The row stays on the Contradictions page with nothing behind it. Entity delete and bulk-delete must dismiss or delete the contradictions that reference the removed versions.

**Person A owns:** `routes/entities.py`, `routes/contradictions.py`, `schemas/entity.py`, `entity_service.py`, `merge_service.py`, `useWorldStore.ts`, `EntityLedger.tsx`, `EntityPanel.tsx`, `Contradictions.tsx`, `mockData.ts`.

## Person B: relationships, timeline, time-slice graph

Person B builds the relationship and event tools, fixes event ordering, and delivers the graph-at-a-chosen-time feature the faculty asked for.

| Priority | Task | Detail |
| --- | --- | --- |
| P0 | Ordering | Sort events by chapter number, then `sequence_index`, then `start_position`, then `created_at`. |
| P0 | Relationships | CRUD in `routes/relationships.py`. A new type on an existing pair adds a version and supersedes the old one (one row per directed pair). Validate that both entities are in the world and source ≠ target. The form has a chapter picker, because a relationship with no chapter has no place on the time axis. |
| P0 | Events and timeline | Event CRUD with participants, `PATCH /events/reorder`, and the timeline UI with up/down buttons (no drag-and-drop). API calls go in a new `src/api/events.ts`. |
| P0 | Time-slice graph | `GET /graph?as_of_chapter=N`, with current behavior as the default (rules below). Stepper or slider over chapter numbers in `WorldGraph.tsx`, with "latest" as the default. |
| P0 | Tests | The as-of rules, including a case where the author resolved a contradiction by keeping the old value. |
| P1 | Timeline click | Clicking a timeline event sets the graph time to that event's chapter. |
| P1 | Manual checks | Call `evaluate_relationship_version` on manual relationships. |

**As-of rules for the graph:**

- **Edges:** take the pair's versions with chapter number ≤ N (no chapter means always visible); the latest wins. Don't use ACTIVE/SUPERSEDED for this, because they describe "now", not "then". Do exclude unresolved CONTRADICTED versions and any version the author rejected, meaning the new-side version of a RESOLVED contradiction that ended up SUPERSEDED. Otherwise the slider shows claims the author threw out.
- **Node properties:** the same rule applied to facts.
- **Nodes:** show a node if it has an as-of fact or edge, a mention at or before N (mention → extraction run → chapter version → chapter), or no chapter-tagged data at all (manual).

**Person B owns:** `routes/relationships.py`, `routes/events.py`, `routes/graph.py`, `schemas/relationship.py`, `schemas/timeline.py`, `schemas/graph.py`, `timeline_service.py`, `graph_service.py`, `WorldGraph.tsx`, `WorldTimeline.tsx`, `src/api/*`.

## Extraction person's tasks

The extraction person fixes event ordering inputs, builds the propose-then-apply flow, and freezes the demo manuscript.

1. Pass `start` into `create_event(start_position=...)`. It is a two-line fix.
2. Make the `RE_EXTRACTION` path run the extractor only, diff against the world via `find_entity`, write the proposals JSON, and serve `routes/proposals.py`.
3. Add the review modal in `WritingRoom.tsx`, calling Person A's and Person B's endpoints. It depends only on the Step 0 contract, so it can be built against stubs.
4. Run the demo manuscript with chapter headings end to end and freeze it as the fixture.

## Conflict rules

These rules keep the three branches from touching the same files.

- Person A and Person B never touch `world_state_service.py`, `pipeline/`, `workers/`, `chapters.py`, `chapter_service.py`, `WritingRoom.tsx` or `ProcessingWorld.tsx`.
- The extraction person never touches `routes/entities.py`, `relationships.py`, `events.py`, or the Person A and Person B pages.
- `router.py`, `App.tsx`, `conftest.py` and `docs/api.md` are frozen after Step 0.
- No model or migration changes on feature branches: the schema is frozen at the `step0` tag.
- Repositories are append-only. New TypeScript types go in new files.
- Person A's merge writes through the models directly, not through Person B's repo methods.
- Branch names follow the repo's `feature/<slug>` pattern, and nobody commits to `main`.

## If time runs out

Cut in this order, and protect everything marked P0, because the faculty asked for the time-slice graph and the demo shows the relationship form and the timeline.

1. Tests.
2. Consistency checks on manual edits.
3. Alias endpoints, retype and bulk delete.
4. The timeline-to-graph click.
5. Edit-triggered extraction. Fallback: an edit saves text only, and the manual tools carry the rest.

**Midpoint gate for the extraction person:** if the proposals diff isn't sane on the demo manuscript by the midpoint, drop to the fallback instead of fighting it in the last days.
