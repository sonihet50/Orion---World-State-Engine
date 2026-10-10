"""
Runs scripts/seed_demo_world.py and checks the data Person A, Person B and the extraction branch build against.
If you change the seed, update EXPECTED_COUNTS and the scenario checks together.
"""
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.core.database import Base
from app.main import app
from app.models import (
    Chapter, ChapterVersion, Contradiction, Entity, EntityAlias, EntityMention, Event, EventParticipant,
    ExtractionRun, Fact, FactVersion, Manuscript, ProcessingJob, Relationship, RelationshipVersion, User, World,
)
from app.services.chapter_service import ChapterService
from scripts import seed_demo_world as seed_script
from scripts.seed_demo_world import sid

EXPECTED_COUNTS = {
    User: 1, World: 1, Manuscript: 1, Chapter: 3, ChapterVersion: 3, ProcessingJob: 1, ExtractionRun: 3,
    Entity: 6, EntityAlias: 8, EntityMention: 11, Fact: 6, FactVersion: 10, Relationship: 8, RelationshipVersion: 10,
    Event: 5, EventParticipant: 9, Contradiction: 2,
}


def _snapshot(db):
    """Every row of every table, as comparable tuples."""
    return {
        table.name: sorted(tuple(repr(v) for v in row) for row in db.execute(table.select()).all())
        for table in Base.metadata.sorted_tables
    }


@pytest.fixture
def seed_args(tmp_path):
    url = f"sqlite:///{(tmp_path / 'demo.db').as_posix()}"
    return url, ["--database-url", url, "--storage-dir", str(tmp_path / "storage")]


@pytest.fixture
def seeded(seed_args):
    url, args = seed_args
    assert seed_script.main(args) == 0
    db = seed_script.make_session(url)
    yield db
    db.close()


def test_seed_counts_and_idempotent(seed_args):
    url, args = seed_args
    assert seed_script.main(args) == 0
    db = seed_script.make_session(url)
    first = _snapshot(db)
    assert {m.__name__: db.query(m).count() for m in EXPECTED_COUNTS} == {
        m.__name__: n for m, n in EXPECTED_COUNTS.items()
    }
    db.close()

    assert seed_script.main(args) == 0   # a second run replaces the world with identical rows
    db = seed_script.make_session(url)
    assert _snapshot(db) == first
    db.close()


def test_chapters_have_text_and_mentions_link_to_chapters(seeded):
    chapters = seeded.query(Chapter).order_by(Chapter.chapter_number).all()
    assert [c.chapter_number for c in chapters] == [1, 2, 3]
    for ch in chapters:
        assert ChapterService(seeded).get_chapter_content(ch.id).startswith(f"Chapter {ch.chapter_number}:")

    # Person B's node rule: mention -> extraction run -> chapter version -> chapter.
    first_seen = {}
    for m in seeded.query(EntityMention).all():
        chapter = m.extraction_run.chapter_version.chapter
        text = ChapterService(seeded).get_chapter_content(chapter.id)
        assert text[m.start_position:m.end_position] == m.surface_text
        first_seen[m.entity_id] = min(first_seen.get(m.entity_id, 99), chapter.chapter_number)
    assert first_seen[sid("entity/ilse")] == 3 and first_seen[sid("entity/saltwind")] == 3
    assert sid("entity/lighthouse") not in first_seen


def test_duplicate_pair_exercises_every_merge_rule(seeded):
    captain, ilse = seeded.get(Entity, sid("entity/captain")), seeded.get(Entity, sid("entity/ilse"))
    assert captain.aliases and ilse.aliases

    def active_role(entity):
        return [v.value for f in entity.facts if f.property_name == "role" for v in f.versions if v.status == "ACTIVE"]
    assert active_role(captain) == ["harbour captain"] and active_role(ilse) == ["recruiter"]   # fold facts

    sail = seeded.get(Event, sid("event/ev_sail"))
    assert {captain.id, ilse.id} <= {p.entity_id for p in sail.participants}                     # drop dup participant

    mara_id = sid("entity/mara")
    pairs = {(r.source_entity_id, r.target_entity_id) for r in seeded.query(Relationship).all()}
    assert (captain.id, mara_id) in pairs and (ilse.id, mara_id) in pairs                         # move versions
    assert (captain.id, ilse.id) in pairs                                                         # self-loop


def test_evolving_fact_and_relationship_type_change(seeded):
    status = seeded.get(Fact, sid("fact/tomas_status"))
    history = sorted(status.versions, key=lambda v: v.created_at)
    assert [(v.chapter.chapter_number, v.value, v.status) for v in history] == [
        (1, "alive", "SUPERSEDED"), (2, "missing", "SUPERSEDED"), (3, "dead", "ACTIVE"),
    ]

    rel = seeded.get(Relationship, sid("relationship/captain_tomas"))
    history = sorted(rel.versions, key=lambda v: v.created_at)
    assert [(v.chapter.chapter_number, v.relationship_type, v.status) for v in history] == [
        (1, "EMPLOYS", "SUPERSEDED"), (2, "ENEMY_OF", "ACTIVE"),
    ]


def test_one_unresolved_and_one_resolved_contradiction(seeded):
    detected = seeded.query(Contradiction).filter_by(status="DETECTED").one()
    assert detected.explanation.startswith("[IMMUTABLE_FACT]")
    assert (detected.old_fact_version.status, detected.new_fact_version.status) == ("ACTIVE", "CONTRADICTED")

    # The author kept the old value: Person B's as-of graph must not show the rejected ENEMY_OF.
    resolved = seeded.query(Contradiction).filter_by(status="RESOLVED").one()
    assert resolved.explanation.startswith("[RELATIONSHIP_INCOMPATIBLE]")
    old, new = resolved.old_relationship_version, resolved.new_relationship_version
    assert (old.relationship_type, old.status) == ("FRIEND_OF", "ACTIVE")
    assert (new.relationship_type, new.status, new.chapter.chapter_number) == ("ENEMY_OF", "SUPERSEDED", 2)


def test_events_and_manual_entity(seeded):
    by_chapter = {}
    for ev in seeded.query(Event).all():
        by_chapter.setdefault(ev.chapter.chapter_number, []).append(ev)
    assert {n: len(evs) for n, evs in by_chapter.items()} == {1: 1, 2: 2, 3: 2}

    # Chapter 2: insertion order is the reverse of text order, so created_at alone sorts it wrong.
    by_text = [e.id for e in sorted(by_chapter[2], key=lambda e: e.start_position)]
    by_created = [e.id for e in sorted(by_chapter[2], key=lambda e: e.created_at)]
    assert by_text == [sid("event/ev_vanish"), sid("event/ev_confront")] and by_created == by_text[::-1]

    lighthouse = seeded.get(Entity, sid("entity/lighthouse"))
    assert not lighthouse.mentions
    versions = [v for f in lighthouse.facts for v in f.versions]
    versions += [v for r in lighthouse.incoming_relationships + lighthouse.outgoing_relationships for v in r.versions]
    assert versions and all(v.chapter_id is None for v in versions)


def test_demo_user_can_read_the_world_through_the_api(seeded):
    app.dependency_overrides[get_db] = lambda: seeded
    try:
        client = TestClient(app)
        login = client.post("/api/v1/auth/login",
                            json={"email": seed_script.DEMO_EMAIL, "password": seed_script.DEMO_PASSWORD})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        world = f"/api/v1/worlds/{seed_script.WORLD_ID}"

        assert client.get(f"{world}/entities", headers=headers).json().__len__() == 6
        assert client.get(f"{world}/timeline", headers=headers).json()["total"] == 5
        assert len(client.get(f"{world}/contradictions", headers=headers).json()) == 2
        graph = client.get(f"{world}/graph", headers=headers)
        assert graph.status_code == 200 and len(graph.json()["nodes"]) == 6
    finally:
        app.dependency_overrides.clear()
