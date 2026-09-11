# Systematic Debugging Protocol & Failure Mode Catalog

> *"When something doesn't work, don't just change random lines hoping for a pass. Isolate the failure, print the intermediate tensors (or state dicts), verify your mental model, and write a test that proves the fix."*
> — Andrej Karpathy Debugging Tenet

---

## 1. The 5-Step Debugging Protocol

1. **Do Not Guess**: Stop making random code edits. Read the exact stack trace, file path, line number, and error message.
2. **Form a Falsifiable Hypothesis**: State clearly: *"I believe line X fails because variable Y is None instead of a dictionary."*
3. **Build the Minimal Reproducer**: Write a 5-line isolated Python snippet or a minimal pytest test case that triggers the exact bug in isolation.
4. **Inspect Ground Truth**: Log or print the actual runtime types, values, and database queries.
5. **Fix the Root Cause & Commit a Regression Test**: Never fix a bug without adding a test that would have caught it.

---

## 2. Catalog of Known Failure Modes & Fixes

### Failure Mode 1: SQLite `OperationalError: no such table` in Tests
- **Symptom**: Pytest fails with `sqlite3.OperationalError: no such table: worlds` even though `Base.metadata.create_all(bind=engine)` was called.
- **Root Cause**: In SQLite, `sqlite:///:memory:` creates a brand new, empty database on *every new connection*. When FastAPI creates a new request-scoped DB session, it connects to a new empty in-memory DB.
- **Fix**: Use `StaticPool` so all sessions share the exact same memory instance:
  ```python
  from sqlalchemy.pool import StaticPool
  test_engine = create_engine(
      "sqlite:///:memory:",
      connect_args={"check_same_thread": False},
      poolclass=StaticPool
  )
  ```

### Failure Mode 2: SQLAlchemy Relationship Name Shadowing
- **Symptom**: `TypeError: '_RelationshipDeclared' object is not callable` inside a model class definition.
- **Root Cause**: Importing `from sqlalchemy.orm import relationship` and then defining a column or attribute named `relationship = relationship(...)`. The attribute reassigns `relationship` in class scope, breaking subsequent relationship definitions.
- **Fix**: Alias the SQLAlchemy import:
  ```python
  from sqlalchemy.orm import relationship as sa_relationship
  relationship = sa_relationship("Relationship", back_populates="versions")
  chapter = sa_relationship("Chapter", back_populates="relationship_versions")
  ```

### Failure Mode 3: Celery Task Serialization `EncodeError`
- **Symptom**: `kombu.exceptions.EncodeError: Object of type World is not JSON serializable`.
- **Root Cause**: Attempting to pass an active SQLAlchemy model instance or session into a Celery task.
- **Fix**: Always pass primitive IDs (strings/UUIDs) and re-query the database inside the worker task:
  ```python
  # INCORRECT:
  extract_chapter_task.delay(world_model_instance)

  # CORRECT:
  extract_chapter_task.delay(world_id=world.id, job_id=job.id)
  ```

### Failure Mode 4: LLM Markdown Code Fence Injection
- **Symptom**: `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` when parsing LLM output.
- **Root Cause**: The LLM output begins with ` ```json ` and ends with ` ``` `.
- **Fix**: Run through [`clean_json_response()`](../app/pipeline/parsers/extraction_parser.py), which strips markdown backticks and extracts the substring between the first `{` and last `}`.

### Failure Mode 5: Python Dictionary Duplicate Key Overwrite
- **Symptom**: In test or graph builders, edges or temporal relations are mysteriously dropped.
- **Root Cause**: Typing duplicate keys in dict literals, e.g. `{"event_1": "ev_1", "event_1": "ev_2"}`. Python silently overwrites earlier keys with the last one.
- **Fix**: Always review dictionary keys for unique names (`event_1`, `event_2`).

### Failure Mode 6: Pydantic V2 Config Deprecation Warnings
- **Symptom**: `PydanticDeprecatedSince20: Support for class-based config is deprecated`.
- **Root Cause**: Using `class Config: from_attributes = True` from Pydantic V1.
- **Fix**: Use Pydantic V2 `ConfigDict`:
  ```python
  from pydantic import BaseModel, ConfigDict

  class EntityResponse(BaseModel):
      model_config = ConfigDict(from_attributes=True)
      id: str
      canonical_name: str
  ```
