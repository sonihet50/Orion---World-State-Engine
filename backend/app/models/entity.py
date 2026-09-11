from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(50), default="unknown", nullable=False)
    canonical_name = Column(String(255), nullable=False)
    source_extraction_id = Column(String(100), nullable=True)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    world = relationship("World", back_populates="entities")
    aliases = relationship("EntityAlias", back_populates="entity", cascade="all, delete-orphan")
    mentions = relationship("EntityMention", back_populates="entity", cascade="all, delete-orphan")
    facts = relationship("Fact", back_populates="entity", cascade="all, delete-orphan")
    outgoing_relationships = relationship(
        "Relationship",
        back_populates="source_entity",
        foreign_keys="Relationship.source_entity_id",
        cascade="all, delete-orphan"
    )
    incoming_relationships = relationship(
        "Relationship",
        back_populates="target_entity",
        foreign_keys="Relationship.target_entity_id",
        cascade="all, delete-orphan"
    )
    event_participants = relationship("EventParticipant", back_populates="entity", cascade="all, delete-orphan")


class EntityAlias(Base):
    __tablename__ = "entity_aliases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String(255), nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)

    entity = relationship("Entity", back_populates="aliases")


class EntityMention(Base):
    __tablename__ = "entity_mentions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    extraction_run_id = Column(String(36), ForeignKey("extraction_runs.id", ondelete="SET NULL"), nullable=True)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    surface_text = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)

    entity = relationship("Entity", back_populates="mentions")
    extraction_run = relationship("ExtractionRun", back_populates="entity_mentions")
