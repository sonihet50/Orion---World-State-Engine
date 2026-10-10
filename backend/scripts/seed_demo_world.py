"""
Seed a small demo world straight through the models, with no extraction.

    cd backend
    python scripts/seed_demo_world.py                                  # DATABASE_URL from .env
    python scripts/seed_demo_world.py --database-url sqlite:///./demo.db

Log in as demo@example.com / orion-demo. The world is "Gull Point (demo)".

Deterministic and idempotent: every row has a fixed uuid5 id and a fixed timestamp. Each run deletes the demo world
(and everything under it) and inserts it again, so running it twice leaves the same rows, and running it again resets
any edits made through the UI. The demo user is created once and then reused.

What it contains, and who needs it:
- 3 chapters, each with one chapter version and one extraction run, written as real text under STORAGE_DIR.
- 6 entities with aliases. "Captain Rook" and "Ilse Rook" are the same person (Person A's merge). Between them they
  hit every merge rule: both have an ACTIVE `role` fact with different values, both take part in the chapter 3
  departure, both KNOW Mara (a duplicate pair after merge), and Captain Rook KNOWS Ilse Rook (a self-loop after merge).
- A fact that evolves: Tomas Hale's `status` is alive (ch 1) -> missing (ch 2) -> dead (ch 3).
- A relationship whose type changes: Captain Rook -> Tomas Hale is EMPLOYS (ch 1) -> ENEMY_OF (ch 2).
- An unresolved contradiction: Mara's `eye_color` is grey (ch 1, ACTIVE), then green (ch 3, CONTRADICTED).
- A resolved contradiction where the author kept the old value: Mara -> Tomas is FRIEND_OF (ch 1, ACTIVE), then
  ENEMY_OF (ch 2, SUPERSEDED). Person B's as-of graph must keep showing FRIEND_OF at chapters 2 and 3.
- A manual entity: Gull Point Lighthouse has no mentions and only chapter-less facts and relationships, so Person B's
  node rule shows it at every chapter.
- 5 events. Chapters 2 and 3 have two events each. In chapter 2 the insertion order (created_at) is the reverse of
  the text order (start_position), so sorting by created_at alone gives the wrong answer.
- Entity mentions are linked mention -> extraction run -> chapter version -> chapter, which Person B's node rule
  follows. "Ilse Rook" and "The Saltwind" are first mentioned in chapter 3, so they appear only from chapter 3 on.
"""
import argparse
import hashlib
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, event, or_  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.config.settings import settings  # noqa: E402
from app.core.constants import ContradictionStatus, ContradictionType, ExtractionRunStatus, JobStatus, JobType  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models import (  # noqa: E402
    Chapter, ChapterVersion, Contradiction, Entity, EntityAlias, EntityMention, Event, EventParticipant,
    ExtractionRun, Fact, FactVersion, Manuscript, ProcessingJob, Relationship, RelationshipVersion, User, World,
)

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "orion-demo"
WORLD_NAME = "Gull Point (demo)"
EXTRACTOR_VERSION = "seed_demo_world"

_NAMESPACE = uuid.UUID("6f1c2a52-3c1e-4d8e-9a57-0d3b5e7a9c11")
# Naive UTC, matching the models' DateTime columns. Fixed so every run writes identical rows.
_BASE_TIME = datetime(2026, 10, 1, 9, 0, 0)
MANUAL = None   # chapter value for data the author added by hand


def sid(key: str) -> str:
    """Stable id for a seeded row."""
    return str(uuid.uuid5(_NAMESPACE, f"orion-demo/{key}"))


def at(chapter: Optional[int], minute: int = 0) -> datetime:
    """Chapter N's extraction happens in hour N; manual edits come afterwards, in hour 4."""
    return _BASE_TIME + timedelta(hours=4 if chapter is None else chapter, minutes=minute)


WORLD_ID = sid("world")

CHAPTERS: List[Tuple[int, str, str]] = [
    (1, "The Lamp", (
        "Chapter 1: The Lamp\n\n"
        "Mara Venn climbed the hundred steps of the lighthouse at dusk, as she did every night. "
        "Tomas Hale was already in the lamp room, trimming the wick. "
        "\"Captain Rook is in the harbour,\" he said. \"She wants the light dark on Thursday.\" "
        "Mara looked at him with her grey eyes and said nothing. "
        "Below them, Captain Rook stood on the pier and watched the lamp come on.\n"
    )),
    (2, "The Storm", (
        "Chapter 2: The Storm\n\n"
        "The storm came on Thursday. Mara kept the lamp burning, and in the morning Tomas was gone. "
        "His coat still hung by the door. "
        "Mara found Captain Rook at the harbour office. \"You told him to put the light out,\" she said. "
        "\"Tomas works for me no longer,\" Rook answered. \"He chose his side.\" "
        "That night Mara wrote in the log that Tomas was missing, and that she would never forgive him.\n"
    )),
    (3, "The Saltwind", (
        "Chapter 3: The Saltwind\n\n"
        "Fishermen pulled Tomas Hale from the water below the point. He was dead. "
        "A week later a woman calling herself Ilse Rook came to the lighthouse and offered Mara passage on the "
        "Saltwind. Her eyes, Mara noticed, were the same green as her own. "
        "Mara signed on as a deckhand, and when the Saltwind sailed, Captain Rook stood at the wheel.\n"
    )),
]

# key: (canonical_name, entity_type, aliases)
ENTITIES: Dict[str, Tuple[str, str, List[str]]] = {
    "mara": ("Mara Venn", "character", ["Mara"]),
    "tomas": ("Tomas Hale", "character", ["Tomas"]),
    "captain": ("Captain Rook", "character", ["Rook", "the Captain"]),
    "ilse": ("Ilse Rook", "character", ["Ilse"]),                                 # duplicate of "captain"
    "lighthouse": ("Gull Point Lighthouse", "location", ["the lighthouse", "Gull Point"]),   # manual
    "saltwind": ("The Saltwind", "object", ["Saltwind"]),
}

# (chapter, entity, surface text); the position is the first occurrence of the surface text in that chapter.
MENTIONS: List[Tuple[int, str, str]] = [
    (1, "mara", "Mara Venn"), (1, "tomas", "Tomas Hale"), (1, "captain", "Captain Rook"),
    (2, "mara", "Mara"), (2, "tomas", "Tomas"), (2, "captain", "Captain Rook"),
    (3, "tomas", "Tomas Hale"), (3, "ilse", "Ilse Rook"), (3, "mara", "Mara"), (3, "saltwind", "Saltwind"),
    (3, "captain", "Captain Rook"),
]

# key: (entity, property_name, [(chapter, value, status), ...] oldest first)
FACTS: Dict[str, Tuple[str, str, List[Tuple[Optional[int], str, str]]]] = {
    "tomas_status": ("tomas", "status", [(1, "alive", "SUPERSEDED"), (2, "missing", "SUPERSEDED"), (3, "dead", "ACTIVE")]),
    "mara_eye_color": ("mara", "eye_color", [(1, "grey", "ACTIVE"), (3, "green", "CONTRADICTED")]),
    "mara_location": ("mara", "location", [(1, "Gull Point Lighthouse", "SUPERSEDED"), (3, "the Saltwind", "ACTIVE")]),
    "captain_role": ("captain", "role", [(1, "harbour captain", "ACTIVE")]),
    "ilse_role": ("ilse", "role", [(3, "recruiter", "ACTIVE")]),
    "lighthouse_built": ("lighthouse", "built", [(MANUAL, "1871", "ACTIVE")]),
}

# key: (source, target, [(chapter, relationship_type, status), ...] oldest first)
RELATIONSHIPS: Dict[str, Tuple[str, str, List[Tuple[Optional[int], str, str]]]] = {
    "mara_tomas": ("mara", "tomas", [(1, "FRIEND_OF", "ACTIVE"), (2, "ENEMY_OF", "SUPERSEDED")]),
    "captain_tomas": ("captain", "tomas", [(1, "EMPLOYS", "SUPERSEDED"), (2, "ENEMY_OF", "ACTIVE")]),
    "mara_lighthouse": ("mara", "lighthouse", [(MANUAL, "LIVES_AT", "ACTIVE")]),
    "tomas_lighthouse": ("tomas", "lighthouse", [(MANUAL, "KEEPER_OF", "ACTIVE")]),
    "captain_mara": ("captain", "mara", [(1, "KNOWS", "ACTIVE")]),
    "ilse_mara": ("ilse", "mara", [(3, "KNOWS", "ACTIVE")]),
    "captain_ilse": ("captain", "ilse", [(3, "KNOWS", "ACTIVE")]),
    "captain_saltwind": ("captain", "saltwind", [(3, "CAPTAIN_OF", "ACTIVE")]),
}

# key: (chapter, created_minute, event_type, sentence from the chapter text, [(entity, role), ...])
# Chapter 2's created_minute order is deliberately the reverse of its text order.
EVENTS: Dict[str, Tuple[int, int, str, str, List[Tuple[str, str]]]] = {
    "ev_lamp": (1, 40, "ARRIVAL", "Captain Rook stood on the pier and watched the lamp come on",
                [("captain", "observer"), ("mara", "keeper")]),
    "ev_vanish": (2, 41, "DISAPPEARANCE", "in the morning Tomas was gone", [("tomas", "missing person")]),
    "ev_confront": (2, 40, "CONFRONTATION", "Mara found Captain Rook at the harbour office",
                    [("mara", "accuser"), ("captain", "accused")]),
    "ev_body": (3, 40, "DISCOVERY", "Fishermen pulled Tomas Hale from the water below the point",
                [("tomas", "victim")]),
    "ev_sail": (3, 41, "DEPARTURE", "when the Saltwind sailed, Captain Rook stood at the wheel",
                [("mara", "deckhand"), ("captain", "captain"), ("ilse", "recruiter")]),
}


def _span(text: str, phrase: str) -> Tuple[int, int]:
    start = text.find(phrase)
    if start < 0:
        raise ValueError(f"seed text is missing {phrase!r}; update the seed data together with the chapter text")
    return start, start + len(phrase)


def _remove_existing_world(db: Session, user_id: str) -> None:
    stale = db.query(World).filter(
        or_(World.id == WORLD_ID, (World.user_id == user_id) & (World.name == WORLD_NAME))
    ).all()
    for world in stale:
        db.delete(world)   # ORM cascades remove everything under the world
    db.flush()


def _get_or_create_user(db: Session) -> User:
    user = db.query(User).filter_by(email=DEMO_EMAIL).first()
    if user is None:
        user = User(id=sid("user"), email=DEMO_EMAIL, password_hash=get_password_hash(DEMO_PASSWORD),
                    created_at=at(0), updated_at=at(0))
        db.add(user)
        db.flush()
    return user


def seed(db: Session, storage_dir: Optional[Path] = None) -> str:
    """Replace the demo world with a fresh copy and commit. Returns the world id."""
    user = _get_or_create_user(db)
    _remove_existing_world(db, user.id)

    world = World(id=WORLD_ID, user_id=user.id, name=WORLD_NAME,
                  description="Seeded demo world for manual-editing, graph and timeline work. Reset with "
                              "scripts/seed_demo_world.py.",
                  created_at=at(0), updated_at=at(0))
    manuscript = Manuscript(id=sid("manuscript"), world=world, title="The Keeper of Gull Point", file_type="txt",
                            created_at=at(0), updated_at=at(0))
    job = ProcessingJob(id=sid("job"), world=world, manuscript=manuscript, job_type=JobType.INITIAL_EXTRACTION.value,
                        status=JobStatus.DONE.value, chapters_total=len(CHAPTERS), chapters_completed=len(CHAPTERS),
                        created_at=at(0, 59), started_at=at(1), completed_at=at(3, 59))
    db.add_all([world, manuscript, job])

    chapter_dir = Path(storage_dir or settings.STORAGE_DIR) / "seed" / WORLD_ID
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapters: Dict[int, Chapter] = {}
    versions: Dict[int, ChapterVersion] = {}
    runs: Dict[int, ExtractionRun] = {}
    texts: Dict[int, str] = {}
    for number, title, text in CHAPTERS:
        path = chapter_dir / f"ch_{number}.txt"
        path.write_bytes(text.encode("utf-8"))
        texts[number] = text
        chapters[number] = Chapter(id=sid(f"chapter/{number}"), manuscript=manuscript, chapter_number=number,
                                   title=title, created_at=at(0, number), updated_at=at(0, number))
        versions[number] = ChapterVersion(id=sid(f"chapter_version/{number}"), chapter=chapters[number],
                                          version_number=1, is_current=True, content_path=str(path.resolve()),
                                          content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                          created_at=at(0, number))
        runs[number] = ExtractionRun(id=sid(f"extraction_run/{number}"), chapter_version=versions[number],
                                     processing_job=job, status=ExtractionRunStatus.DONE.value,
                                     extractor_version=EXTRACTOR_VERSION, created_by=user.id,
                                     created_at=at(number), started_at=at(number), completed_at=at(number, 30))
    db.add_all([*chapters.values(), *versions.values(), *runs.values()])

    first_chapter = {key: min((c for c, k, _ in MENTIONS if k == key), default=None) for key in ENTITIES}
    entities: Dict[str, Entity] = {}
    for i, (key, (name, entity_type, aliases)) in enumerate(ENTITIES.items()):
        ch = first_chapter[key]
        entities[key] = Entity(id=sid(f"entity/{key}"), world=world, canonical_name=name, entity_type=entity_type,
                               source_extraction_id=runs[ch].id if ch else None,
                               provenance=f"Chapter {ch}" if ch else "Added manually",
                               created_at=at(ch, i), updated_at=at(ch, i))
        entities[key].aliases = [EntityAlias(id=sid(f"alias/{key}/{alias}"), alias=alias, confidence=1.0)
                                 for alias in aliases]
    db.add_all(entities.values())

    for ch, key, surface in MENTIONS:
        start, end = _span(texts[ch], surface)
        db.add(EntityMention(id=sid(f"mention/{ch}/{key}/{surface}"), extraction_run=runs[ch], entity=entities[key],
                             surface_text=surface, start_position=start, end_position=end, confidence=1.0))

    fact_versions: Dict[Tuple[str, int], FactVersion] = {}
    for key, (entity_key, prop, history) in FACTS.items():
        fact = Fact(id=sid(f"fact/{key}"), entity=entities[entity_key], property_name=prop,
                    created_at=at(history[0][0], 10))
        db.add(fact)
        for n, (ch, value, status) in enumerate(history):
            fact_versions[(key, n)] = FactVersion(
                id=sid(f"fact_version/{key}/{n}"), fact=fact, value=value, status=status, confidence=1.0,
                chapter=chapters[ch] if ch else None, chapter_version=versions[ch] if ch else None,
                extraction_run=runs[ch] if ch else None, created_at=at(ch, 10 + n))
            db.add(fact_versions[(key, n)])

    rel_versions: Dict[Tuple[str, int], RelationshipVersion] = {}
    for key, (source, target, history) in RELATIONSHIPS.items():
        first_ch = history[0][0]
        rel = Relationship(id=sid(f"relationship/{key}"), world=world, source_entity=entities[source],
                           target_entity=entities[target], source_extraction_id=runs[first_ch].id if first_ch else None,
                           created_at=at(first_ch, 20))
        db.add(rel)
        for n, (ch, rel_type, status) in enumerate(history):
            rel_versions[(key, n)] = RelationshipVersion(
                id=sid(f"relationship_version/{key}/{n}"), relationship=rel, relationship_type=rel_type,
                status=status, confidence=1.0, chapter=chapters[ch] if ch else None,
                chapter_version=versions[ch] if ch else None, extraction_run=runs[ch] if ch else None,
                created_at=at(ch, 20 + n))
            db.add(rel_versions[(key, n)])

    for key, (ch, minute, event_type, sentence, participants) in EVENTS.items():
        start, end = _span(texts[ch], sentence)
        ev = Event(id=sid(f"event/{key}"), world=world, chapter=chapters[ch], chapter_version=versions[ch],
                   extraction_run=runs[ch], event_type=event_type, description=sentence[0].upper() + sentence[1:] + ".",
                   start_position=start, end_position=end, confidence=1.0, created_at=at(ch, minute))
        ev.participants = [EventParticipant(id=sid(f"participant/{key}/{entity_key}"), entity=entities[entity_key],
                                            role=role) for entity_key, role in participants]
        db.add(ev)

    # Same explanation format the consistency engine records: "[RULE_ID] text".
    db.add(Contradiction(
        id=sid("contradiction/mara_eye_color"), world=world, contradiction_type=ContradictionType.FACT_FACT.value,
        old_fact_version=fact_versions[("mara_eye_color", 0)], new_fact_version=fact_versions[("mara_eye_color", 1)],
        explanation="[IMMUTABLE_FACT] Direct contradiction for 'Mara Venn': property 'eye_color' was previously "
                    "stated as 'grey' but is now stated as 'green'.",
        confidence=0.9, status=ContradictionStatus.DETECTED.value, created_at=at(3, 11)))
    db.add(Contradiction(
        id=sid("contradiction/mara_tomas"), world=world,
        contradiction_type=ContradictionType.RELATIONSHIP_RELATIONSHIP.value,
        old_relationship_version=rel_versions[("mara_tomas", 0)],
        new_relationship_version=rel_versions[("mara_tomas", 1)],
        explanation="[RELATIONSHIP_INCOMPATIBLE] Relationship conflict between 'Mara Venn' and 'Tomas Hale': "
                    "previous relationship 'FRIEND_OF' is fundamentally incompatible with new 'ENEMY_OF'.",
        confidence=0.85, status=ContradictionStatus.RESOLVED.value, created_at=at(2, 21)))

    db.commit()
    return WORLD_ID


def make_session(database_url: str) -> Session:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    if database_url.startswith("sqlite"):
        # Enforce foreign keys like Postgres does, so a bad cascade fails here too.
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(bind=engine)   # same as the app's startup init_db()
    return sessionmaker(bind=engine, autoflush=False)()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the deterministic Gull Point demo world.")
    parser.add_argument("--database-url", default=settings.DATABASE_URL,
                        help="defaults to DATABASE_URL from the environment / .env")
    parser.add_argument("--storage-dir", type=Path, default=None,
                        help="where chapter text is written (defaults to STORAGE_DIR)")
    args = parser.parse_args(argv)

    db = make_session(args.database_url)
    try:
        world_id = seed(db, args.storage_dir)
    finally:
        db.close()
    print(f"Seeded '{WORLD_NAME}' ({world_id}). Log in as {DEMO_EMAIL} / {DEMO_PASSWORD}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
