---
name: add-api-endpoint
description: Step-by-step recipe to safely add a new REST API endpoint across all backend layers.
---

# Skill: Adding a New REST API Endpoint

Follow this exact recipe whenever adding a new feature or endpoint.

---

## The 5-Step Recipe

```
[1. Pydantic Schema] ──> [2. Repository Method] ──> [3. Service Logic] ──> [4. Route Handler] ──> [5. Pytest Test]
```

### Step 1: Define Schemas in `app/schemas/`
Create typed request and response models with Pydantic V2 `ConfigDict`:

```python
# app/schemas/feature.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FeatureCreate(BaseModel):
    title: str

class FeatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
```

### Step 2: Add Database Queries in `app/repositories/`
Add specialized query methods to the appropriate repository (or [`BaseRepository`](../../app/repositories/base.py)):

```python
# app/repositories/feature_repo.py
from app.repositories.base import BaseRepository
from app.models.feature import Feature

class FeatureRepository(BaseRepository[Feature]):
    def get_by_title(self, world_id: str, title: str):
        return self.db.query(Feature).filter_by(world_id=world_id, title=title).first()
```

### Step 3: Implement Business Logic in `app/services/`
Coordinate validation, transactions, and state mutations:

```python
# app/services/feature_service.py
class FeatureService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FeatureRepository(db)

    def create_feature(self, world_id: str, title: str):
        return self.repo.create({"world_id": world_id, "title": title})
```

### Step 4: Expose Route in `app/api/v1/routes/`
Add the router endpoint with proper status codes and dependency injection:

```python
# app/api/v1/routes/features.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_optional

router = APIRouter()

@router.post("/{world_id}/features", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature(world_id: str, payload: FeatureCreate, db: Session = Depends(get_db)):
    service = FeatureService(db)
    return service.create_feature(world_id, payload.title)
```

Ensure the router is registered in [`app/api/v1/router.py`](../../app/api/v1/router.py):
```python
api_router.include_router(features_router, prefix="/worlds", tags=["Features"])
```

### Step 5: Write the Regression Test in `app/tests/test_api.py`
```python
def test_create_feature():
    resp = client.post("/api/v1/worlds/world-1/features", json={"title": "Magic System"})
    assert resp.status_code == 201
    assert resp.json()["title"] == "Magic System"
```

---

## Verification

Run pytest to verify the new route:
```bash
PYTHONPATH=backend pytest app/tests/test_api.py -v
```
