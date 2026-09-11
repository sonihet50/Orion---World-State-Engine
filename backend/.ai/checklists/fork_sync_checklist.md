# Fork Synchronization Checklist

Run through this checklist whenever pulling upstream changes into this fork repository.

---

## 1. Remote Verification
- [ ] Verify `upstream` remote is configured:
  ```bash
  git remote -v
  ```

## 2. Synchronization Protocol
- [ ] Commit or stash any uncommitted local work:
  ```bash
  git status
  ```
- [ ] Fetch all upstream branches:
  ```bash
  git fetch upstream
  ```
- [ ] Rebase local `main` onto `upstream/main`:
  ```bash
  git checkout main
  git rebase upstream/main
  ```

## 3. Migration & Conflict Verification
- [ ] Check Alembic migration history for duplicate branch heads:
  ```bash
  cd backend
  alembic history
  ```
- [ ] If multiple heads exist, resolve `down_revision` pointers or merge with:
  ```bash
  alembic merge heads -m "merge_upstream_migrations"
  ```
- [ ] Run full test suite to verify upstream changes did not break local logic:
  ```bash
  PYTHONPATH=backend pytest app/tests/ -v
  ```
