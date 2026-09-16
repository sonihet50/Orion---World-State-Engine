import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.core.database import Base
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.services.world_state_service import WorldStateService

# Set up dedicated in-memory DB for security tests
sec_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SecSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sec_engine)
Base.metadata.create_all(bind=sec_engine)

def override_sec_db():
    db = SecSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_sec_test_overrides():
    app.dependency_overrides[get_db] = override_sec_db
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_users():
    db = SecSessionLocal()
    # Create User 1
    u1 = User(
        id="user-1-id",
        email="user1@example.com",
        password_hash=get_password_hash("Password123!")
    )
    # Create User 2
    u2 = User(
        id="user-2-id",
        email="user2@example.com",
        password_hash=get_password_hash("Password123!")
    )
    db.add_all([u1, u2])
    db.commit()
    db.close()

@pytest.fixture
def auth_headers_user1():
    token = create_access_token("user-1-id")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_user2():
    token = create_access_token("user-2-id")
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_requests_blocked():
    """All core endpoints must reject unauthenticated requests with 401."""
    # List worlds
    resp = client.get("/api/v1/worlds")
    assert resp.status_code == 401

    # Create world
    resp = client.post("/api/v1/worlds", json={"name": "Forbidden Realm"})
    assert resp.status_code == 401

    # Chat
    resp = client.post("/api/v1/worlds/some-id/chat", json={"message": "hello"})
    assert resp.status_code == 401

    # Entities
    resp = client.get("/api/v1/worlds/some-id/entities")
    assert resp.status_code == 401


def test_duplicate_world_name_blocked(auth_headers_user1, auth_headers_user2):
    """A user cannot create worlds with duplicate names, but different users can."""
    # 1. User 1 creates "Valinor"
    resp = client.post(
        "/api/v1/worlds",
        json={"name": "Valinor", "description": "Immortal Lands"},
        headers=auth_headers_user1
    )
    assert resp.status_code == 201

    # 2. User 1 creates "Valinor" again -> 400 Bad Request
    dup_resp = client.post(
        "/api/v1/worlds",
        json={"name": "Valinor", "description": "Duplicate"},
        headers=auth_headers_user1
    )
    assert dup_resp.status_code == 400
    assert "already exists" in dup_resp.json()["detail"].lower()

    # 3. User 1 creates "  valinor  " (case-insensitive and trimmed) -> 400 Bad Request
    case_resp = client.post(
        "/api/v1/worlds",
        json={"name": "  valinor  ", "description": "Duplicate with spaces"},
        headers=auth_headers_user1
    )
    assert case_resp.status_code == 400

    # 4. User 2 creates "Valinor" -> 201 Created (allowed for different user)
    u2_resp = client.post(
        "/api/v1/worlds",
        json={"name": "Valinor", "description": "User 2's realm"},
        headers=auth_headers_user2
    )
    assert u2_resp.status_code == 201


def test_cross_tenant_isolation(auth_headers_user1, auth_headers_user2):
    """User 2 cannot view, mutate, or delete User 1's world and child resources."""
    # Create world as User 1
    resp = client.post(
        "/api/v1/worlds",
        json={"name": "Gondor"},
        headers=auth_headers_user1
    )
    assert resp.status_code == 201
    gondor_id = resp.json()["id"]

    # User 2 tries to GET User 1's world -> 404
    get_resp = client.get(f"/api/v1/worlds/{gondor_id}", headers=auth_headers_user2)
    assert get_resp.status_code == 404

    # User 2 tries to UPDATE User 1's world -> 404
    put_resp = client.put(
        f"/api/v1/worlds/{gondor_id}",
        json={"name": "Hacked Gondor"},
        headers=auth_headers_user2
    )
    assert put_resp.status_code == 404

    # User 2 tries to DELETE User 1's world -> 404
    del_resp = client.delete(f"/api/v1/worlds/{gondor_id}", headers=auth_headers_user2)
    assert del_resp.status_code == 404

    # User 2 tries to access User 1's chat -> 404
    chat_resp = client.post(
        f"/api/v1/worlds/{gondor_id}/chat",
        json={"message": "Who is king?"},
        headers=auth_headers_user2
    )
    assert chat_resp.status_code == 404


def test_world_name_whitespace_validation(auth_headers_user1):
    """Empty or whitespace-only world names must be rejected with 422."""
    resp = client.post(
        "/api/v1/worlds",
        json={"name": "   "},
        headers=auth_headers_user1
    )
    assert resp.status_code == 422

    resp2 = client.post(
        "/api/v1/worlds",
        json={"name": ""},
        headers=auth_headers_user1
    )
    assert resp2.status_code == 422


def test_duplicate_entity_name_blocked(auth_headers_user1):
    """Cannot create two entities with the same canonical name in the same world."""
    # Create world
    w_resp = client.post(
        "/api/v1/worlds",
        json={"name": "Rohan"},
        headers=auth_headers_user1
    )
    assert w_resp.status_code == 201
    world_id = w_resp.json()["id"]

    # Create entity "Eomer"
    ent_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities",
        json={"canonical_name": "Eomer", "entity_type": "character"},
        headers=auth_headers_user1
    )
    assert ent_resp.status_code == 201

    # Attempt to create duplicate "Eomer"
    dup_ent_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities",
        json={"canonical_name": "Eomer", "entity_type": "character"},
        headers=auth_headers_user1
    )
    assert dup_ent_resp.status_code == 400
    assert "already exists" in dup_ent_resp.json()["detail"].lower()


def test_empty_manuscript_upload_rejected(auth_headers_user1):
    """Uploading a 0-byte file must be rejected with 400."""
    w_resp = client.post(
        "/api/v1/worlds",
        json={"name": "Rivendell"},
        headers=auth_headers_user1
    )
    world_id = w_resp.json()["id"]

    empty_file = ("empty.txt", BytesIO(b""), "text/plain")
    resp = client.post(
        f"/api/v1/worlds/{world_id}/manuscripts",
        files={"file": empty_file},
        headers=auth_headers_user1
    )
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()


def test_fact_deletion_idor_protection(auth_headers_user1):
    """Fact deletion must verify that the fact belongs to the entity in the world."""
    # Create world
    w_resp = client.post(
        "/api/v1/worlds",
        json={"name": "Mordor"},
        headers=auth_headers_user1
    )
    world_id = w_resp.json()["id"]

    # Create Entity 1
    e1_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities",
        json={"canonical_name": "Sauron"},
        headers=auth_headers_user1
    )
    e1_id = e1_resp.json()["id"]

    # Create Entity 2
    e2_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities",
        json={"canonical_name": "Nazgul"},
        headers=auth_headers_user1
    )
    e2_id = e2_resp.json()["id"]

    # Add fact to Entity 2
    f2_resp = client.post(
        f"/api/v1/worlds/{world_id}/entities/{e2_id}/facts",
        json={"property_name": "mount", "value": "Fellbeast"},
        headers=auth_headers_user1
    )
    assert f2_resp.status_code == 201

    # Fetch entity 2 to get fact_id
    detail_resp = client.get(f"/api/v1/worlds/{world_id}/entities/{e2_id}", headers=auth_headers_user1)
    fact2_id = detail_resp.json()["facts"][0]["id"]

    # Attempt to delete fact2 using Entity 1's URL -> 404 Not Found (IDOR blocked)
    idor_del = client.delete(
        f"/api/v1/worlds/{world_id}/entities/{e1_id}/facts/{fact2_id}",
        headers=auth_headers_user1
    )
    assert idor_del.status_code == 404


def test_fact_version_status_progression():
    """Valid evolution of a mutable attribute supersedes old version and activates new version."""
    db = SecSessionLocal()
    service = WorldStateService(db)

    # 1. First extraction with status "Apprentice"
    data1 = {
        "entities": [{
            "canonical_name": "Luke Skywalker",
            "type": "character",
            "attributes": {"rank": "Apprentice"}
        }],
        "relationships": [],
        "events": []
    }
    service.integrate_extraction_result("world-test-evol", data1)

    ent = service.entity_repo.get_by_canonical("world-test-evol", "Luke Skywalker")
    assert ent is not None
    fact = service.fact_repo.get_or_create_fact(ent.id, "rank")
    assert len(fact.versions) == 1
    assert fact.versions[0].status == "ACTIVE"
    assert fact.versions[0].value == "Apprentice"

    # 2. Second extraction with status "Jedi Knight"
    data2 = {
        "entities": [{
            "canonical_name": "Luke Skywalker",
            "type": "character",
            "attributes": {"rank": "Jedi Knight"}
        }],
        "relationships": [],
        "events": []
    }
    service.integrate_extraction_result("world-test-evol", data2)

    db.refresh(fact)
    assert len(fact.versions) == 2
    # Verify the old version is SUPERSEDED and new version is ACTIVE
    active_v = service.fact_repo.get_active_version(fact.id)
    assert active_v is not None
    assert active_v.value == "Jedi Knight"
    assert active_v.status == "ACTIVE"

    old_v = [v for v in fact.versions if v.value == "Apprentice"][0]
    assert old_v.status == "SUPERSEDED"

    db.close()
