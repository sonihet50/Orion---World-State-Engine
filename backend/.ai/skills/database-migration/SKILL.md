---
name: database-migration
description: Safely modify SQLAlchemy models, generate revisions, and apply Alembic migrations.
---

# Skill: Database Migrations with Alembic

Follow this recipe whenever modifying table columns, adding tables, or altering constraints in [`app/models/`](../../app/models/).

---

## The Safe Migration Workflow

```
[1. Modify Model] ──> [2. Generate Revision] ──> [3. Review Script] ──> [4. Upgrade Head] ──> [5. Test Rollback]
```

### Step 1: Update the Model Class
Modify the model in `app/models/` (e.g. adding a new column):
```python
# app/models/entity.py
summary = Column(Text, nullable=True)
```
Ensure it's re-exported in [`app/models/__init__.py`](../../app/models/__init__.py).

### Step 2: Auto-Generate Alembic Migration
Run Alembic with a descriptive message from the `backend/` root:
```bash
cd backend
PYTHONPATH=. alembic revision --autogenerate -m "add_summary_to_entities"
```

### Step 3: Inspect the Generated Script in `alembic/versions/`
Open the newly created revision file and verify:
- `upgrade()` applies the exact expected change (`op.add_column(...)`).
- `downgrade()` properly reverses the change (`op.drop_column(...)`).
- No extraneous or accidental drops are present.

### Step 4: Apply Migration
```bash
alembic upgrade head
```

### Step 5: Verify Schema & Rollback
Test that rollback works cleanly without leaving database artifacts:
```bash
alembic downgrade -1
alembic upgrade head
```

---

## Verification

Run all backend tests against the updated models:
```bash
PYTHONPATH=backend pytest app/tests/ -v
```
