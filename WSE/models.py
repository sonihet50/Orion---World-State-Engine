import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    worlds = relationship("World", back_populates="user")

class World(Base):
    __tablename__ = "worlds"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="worlds")
    manuscripts = relationship("Manuscript", back_populates="world")
    jobs = relationship("Job", back_populates="world")
    entities = relationship("Entity", back_populates="world")
    relationships = relationship("Relationship", back_populates="world")

class Manuscript(Base):
    __tablename__ = "manuscripts"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    title = Column(String)
    original_file_path = Column(Text)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    world = relationship("World", back_populates="manuscripts")
    versions = relationship("ManuscriptVersion", back_populates="manuscript")

class ManuscriptVersion(Base):
    __tablename__ = "manuscript_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    manuscript_id = Column(String, ForeignKey("manuscripts.id"))
    version_number = Column(Integer)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    manuscript = relationship("Manuscript", back_populates="versions")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(String, primary_key=True, default=generate_uuid)
    manuscript_id = Column(String, ForeignKey("manuscripts.id"))
    chapter_number = Column(Integer)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChapterVersion(Base):
    __tablename__ = "chapter_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    chapter_id = Column(String, ForeignKey("chapters.id"))
    version_number = Column(Integer)
    is_current = Column(Boolean)
    content_path = Column(Text)
    content_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    manuscript_id = Column(String, ForeignKey("manuscripts.id"), nullable=True)
    type = Column(String) # job_type
    status = Column(String) # queued, processing, done, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer, default=0)

    world = relationship("World", back_populates="jobs")

class ExtractionRun(Base):
    __tablename__ = "extraction_runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    chapter_version_id = Column(String, ForeignKey("chapter_versions.id"))
    processing_job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    status = Column(String)
    extractor_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

class Entity(Base):
    __tablename__ = "entities"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    entity_type = Column(String)
    canonical_name = Column(String)
    source_extraction_id = Column(String, nullable=True) # debug field for pipeline's internal ID
    provenance = Column(Text, nullable=True) # JSON array of source chunk IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    world = relationship("World", back_populates="entities")

class EntityAlias(Base):
    __tablename__ = "entity_aliases"
    id = Column(String, primary_key=True, default=generate_uuid)
    entity_id = Column(String, ForeignKey("entities.id"))
    alias = Column(String)
    confidence = Column(Float)

class EntityMention(Base):
    __tablename__ = "entity_mentions"
    id = Column(String, primary_key=True, default=generate_uuid)
    extraction_run_id = Column(String, ForeignKey("extraction_runs.id"), nullable=True)
    entity_id = Column(String, ForeignKey("entities.id"))
    surface_text = Column(Text)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float)

class Fact(Base):
    __tablename__ = "facts"
    id = Column(String, primary_key=True, default=generate_uuid)
    entity_id = Column(String, ForeignKey("entities.id"))
    property_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class FactVersion(Base):
    __tablename__ = "fact_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    fact_id = Column(String, ForeignKey("facts.id"))
    chapter_id = Column(String, ForeignKey("chapters.id"), nullable=True)
    chapter_version_id = Column(String, ForeignKey("chapter_versions.id"), nullable=True)
    extraction_run_id = Column(String, ForeignKey("extraction_runs.id"), nullable=True)
    value = Column(JSONB)
    status = Column(String) # ACTIVE / SUPERSEDED / CONTRADICTED
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class FactMention(Base):
    __tablename__ = "fact_mentions"
    id = Column(String, primary_key=True, default=generate_uuid)
    extraction_run_id = Column(String, ForeignKey("extraction_runs.id"), nullable=True)
    entity_id = Column(String, ForeignKey("entities.id"))
    property_name = Column(String)
    value = Column(JSONB)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float)

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    source_entity_id = Column(String, ForeignKey("entities.id"))
    target_entity_id = Column(String, ForeignKey("entities.id"))
    source_extraction_id = Column(String, nullable=True) # debug field
    created_at = Column(DateTime, default=datetime.utcnow)

    world = relationship("World", back_populates="relationships")

class RelationshipVersion(Base):
    __tablename__ = "relationship_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    relationship_id = Column(String, ForeignKey("relationships.id"))
    chapter_id = Column(String, ForeignKey("chapters.id"), nullable=True)
    chapter_version_id = Column(String, ForeignKey("chapter_versions.id"), nullable=True)
    extraction_run_id = Column(String, ForeignKey("extraction_runs.id"), nullable=True)
    relationship_type = Column(String)
    status = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    chapter_id = Column(String, ForeignKey("chapters.id"), nullable=True)
    chapter_version_id = Column(String, ForeignKey("chapter_versions.id"), nullable=True)
    extraction_run_id = Column(String, ForeignKey("extraction_runs.id"), nullable=True)
    event_type = Column(String)
    description = Column(Text)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class EventParticipant(Base):
    __tablename__ = "event_participants"
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.id"))
    entity_id = Column(String, ForeignKey("entities.id"))
    role = Column(String)

class Contradiction(Base):
    __tablename__ = "contradictions"
    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"))
    contradiction_type = Column(String)
    old_fact_version_id = Column(String, ForeignKey("fact_versions.id"), nullable=True)
    new_fact_version_id = Column(String, ForeignKey("fact_versions.id"), nullable=True)
    old_relationship_version_id = Column(String, ForeignKey("relationship_versions.id"), nullable=True)
    new_relationship_version_id = Column(String, ForeignKey("relationship_versions.id"), nullable=True)
    event_id_a = Column(String, ForeignKey("events.id"), nullable=True)
    event_id_b = Column(String, ForeignKey("events.id"), nullable=True)
    explanation = Column(Text)
    confidence = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
