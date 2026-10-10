# Claude Code Instructions — Orion World State Engine (repo root)

This repo has a FastAPI backend (`backend/`), a React + Vite frontend (`Frontend/`) and a local extractor package
(`extractor/`). The agent rules live under `backend/`. They are imported here so a session started at the repo root
loads them too.

## Always load

- Backend instructions and the `.ai/` rule system: @backend/CLAUDE.md
- Work split, file ownership and frozen files: @backend/.ai/SPLIT.md

Paths in `backend/CLAUDE.md` (such as `.ai/RULES.md`) are relative to `backend/`.

## Before editing any file

1. Find the file in `backend/.ai/SPLIT.md`. If your branch doesn't own it, or it is frozen, stop and ask.
2. **No model or migration changes on feature branches.** The repo has exactly one Alembic head (`ef5362e51e02`).
   Two branches that each add a migration would create two heads. Only `feature/step0-scaffold` may change
   `backend/app/models/` or `backend/alembic/versions/` (SPLIT.md Rule S.1).
3. Follow `backend/.ai/RULES.md`. Rule 3.4 covers author-initiated edits, merges and deletes.

## Commands (run from the repo root)

```bash
# Backend tests: must be 0 failures before any commit (RULES.md 7.1)
cd backend && PYTHONPATH=. pytest app/tests/ -q

# Frontend build and lint
cd Frontend && npm run build && npm run lint
```
