---
name: test-driven-verification
description: Recipe for writing unit, integration, and API tests with pytest, SQLite StaticPool, and mocks.
---

# Skill: Test-Driven Verification

Follow this guide when writing tests or verifying system integrity before declaring tasks complete.

---

## 1. Test Architecture

The backend test suite is organized into three focused modules in [`app/tests/`](../../app/tests/):
- **`test_api.py`**: End-to-end HTTP request/response validation using FastAPI `TestClient`.
- **`test_services.py`**: Business logic, domain invariants, and rule-based consistency checks.
- **`test_pipeline.py`**: Token splitting, JSON repair, coreference resolution, and prompt adherence.

---

## 2. In-Memory SQLite Fixture Standard

Always use `StaticPool` for in-memory SQLite testing to guarantee all connections share the same database instance:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base

@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
```

---

## 3. Mocking External LLM Calls

Never hit live paid APIs or expect external Ollama servers during unit testing. Use the built-in Mock provider or `unittest.mock`:

```python
from unittest.mock import patch

def test_extraction_with_mock():
    with patch("app.pipeline.llm_client.llm_client.generate") as mock_gen:
        mock_gen.return_value = '{"entities": [{"canonical_name": "Hero", "type": "character"}]}'
        result = orchestrator.extract_chapter("Chapter text here...")
        assert len(result["entities"]) == 1
```

---

## 4. Verification Commands

```bash
# Run all tests with verbose output
PYTHONPATH=backend pytest app/tests/ -v

# Run with fail-fast (stop on first failure)
PYTHONPATH=backend pytest app/tests/ -x

# Run only tests matching a keyword
PYTHONPATH=backend pytest app/tests/ -k "contradiction"
```
