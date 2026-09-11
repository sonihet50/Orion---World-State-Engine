import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.core.database import Base

# Setup in-memory test database with StaticPool so all connections share the same memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_worlds_crud():
    # 1. Create world
    resp = client.post("/api/v1/worlds", json={"name": "Eldoria", "description": "High fantasy realm"})
    assert resp.status_code == 201
    world_data = resp.json()
    world_id = world_data["id"]
    assert world_data["name"] == "Eldoria"

    # 2. List worlds
    list_resp = client.get("/api/v1/worlds")
    assert list_resp.status_code == 200
    assert any(w["id"] == world_id for w in list_resp.json())

    # 3. Get specific world
    get_resp = client.get(f"/api/v1/worlds/{world_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Eldoria"

def test_entity_endpoints():
    # Create world first
    w_resp = client.post("/api/v1/worlds", json={"name": "Cyberia"})
    assert w_resp.status_code == 201
    world_id = w_resp.json()["id"]

    # Create entity
    ent_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities",
        json={
            "canonical_name": "Major Motoko",
            "entity_type": "character",
            "aliases": ["The Major"],
            "attributes": {"rank": "Major"}
        }
    )
    assert ent_resp.status_code == 201
    ent_id = ent_resp.json()["id"]

    # List entities
    list_resp = client.get(f"/api/v1/worlds/{world_id}/entities")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Graph
    graph_resp = client.get(f"/api/v1/worlds/{world_id}/graph")
    assert graph_resp.status_code == 200
    assert len(graph_resp.json()["nodes"]) == 1

    # Chat
    chat_resp = client.post(
        f"/api/v1/worlds/{world_id}/chat",
        json={"message": "Who is Major Motoko?"}
    )
    assert chat_resp.status_code == 200
    assert "response" in chat_resp.json()
