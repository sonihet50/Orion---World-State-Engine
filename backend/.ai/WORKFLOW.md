# Git Repository Structure & Fork Workflow

> **FORK NOTICE**: This repository is a **fork** of the upstream Orion project. When operating as an AI agent, you must follow strict fork hygiene to prevent branch divergence, merge conflicts, and un-rebasable commit histories.

---

## 1. Remote Topology

Before starting any branch work, verify configured remotes:

```bash
git remote -v
```

Expected setup:
- **`origin`**: Your personal/fork repository (where you push branches and open pull requests).
- **`upstream`**: The original source repository (from which you pull upstream fixes and features).

If `upstream` is not yet configured:
```bash
git remote add upstream <upstream-repo-url>
git fetch upstream
```

---

## 2. Branching Strategy

| Branch Pattern | Purpose | Example |
|---|---|---|
| `main` | Production-ready, stable tracking branch | `main` |
| `feature/<slug>` | New features or endpoints | `feature/srs-search-endpoint` |
| `fix/<slug>` | Targeted bug fixes or schema corrections | `fix/temporal-cycle-detection` |
| `refactor/<slug>` | Structural improvements with zero behavior changes | `refactor/pydantic-v2-migration` |
| `test/<slug>` | Test suite additions or coverage improvements | `test/add-manuscript-service-tests` |

**Rule**: Never commit directly to `main`. Always create a descriptive branch:
```bash
git checkout -b feature/srs-export-pipeline
```

---

## 3. Atomic Commit Standards

We adhere to the **Conventional Commits** specification:

```
<type>(<scope>): <short imperative summary>

[optional body explaining motivation and non-obvious details]

[optional footer(s), e.g., Closes #123]
```

### Allowed Types
- **`feat`**: A new feature (e.g., `feat(api): add chapter comparison diff endpoint (REQ-34)`)
- **`fix`**: A bug fix (e.g., `fix(consistency): resolve false-positive in location clash check`)
- **`refactor`**: Code restructuring without API or behavior change
- **`test`**: Adding missing tests or correcting test assertions
- **`docs`**: Documentation only (`.ai/`, `README.md`, docstrings)
- **`chore`**: Tooling, dependencies, or `.gitignore` changes

### Commit Rules for AI Agents
1. **One Logical Change Per Commit**: Do not bundle a database migration, an unrelated route tweak, and a documentation fix into one single commit.
2. **Never Commit Secrets or Local Artifacts**: Ensure `.venv`, `storage/`, `__pycache__`, `.pytest_cache`, and `.env` secrets are never staged.
3. **Green Tests Before Every Commit**: You must run `PYTHONPATH=backend pytest app/tests/ -v` and verify 0 failures prior to executing `git commit`.

---

## 4. Fork Synchronization Protocol (Clean Rebase)

To keep this fork synchronized with upstream without generating messy merge bubbles:

```bash
# 1. Fetch latest commits from upstream
git fetch upstream

# 2. Rebase local main onto upstream main
git checkout main
git rebase upstream/main

# 3. Rebase active feature branch onto updated main
git checkout feature/your-feature
git rebase main
```

---

## 5. Merge Conflict Resolution Heuristics

When a rebase or merge encounters conflicts:

1. **Never Blindly Choose `--ours` or `--theirs`**:
   Examine every conflicted chunk with `git diff`. Understand the intent of both commits.
2. **Alembic Migration Conflicts**:
   If upstream added a migration while your branch added one, both files will claim the same `down_revision`.
   - Update your migration's `down_revision` to point to the new upstream migration's revision ID.
   - Verify linear history with `alembic history`.
3. **Model & Schema Conflicts**:
   Ensure no required fields were dropped and no enum statuses conflict.
4. **Post-Conflict Verification**:
   After resolving conflicts, run the test suite immediately:
   ```bash
   PYTHONPATH=backend pytest app/tests/ -v
   git rebase --continue
   ```
