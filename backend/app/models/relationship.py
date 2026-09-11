from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    source_entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    target_entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    source_extraction_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    world = sa_relationship("World", back_populates="relationships")
    source_entity = sa_relationship("Entity", foreign_keys=[source_entity_id], back_populates="outgoing_relationships")
    target_entity = sa_relationship("Entity", foreign_keys=[target_entity_id], back_populates="incoming_relationships")
    versions = sa_relationship("RelationshipVersion", back_populates="relationship", cascade="all, delete-orphan", order_by="RelationshipVersion.created_at.desc()")


class RelationshipVersion(Base):
    __tablename__ = "relationship_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    relationship_id = Column(String(36), ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id", ondelete="SET NULL"), nullable=True)
    extraction_run_id = Column(String(36), ForeignKey("extraction_runs.id", ondelete="SET NULL"), nullable=True)
    relationship_type = Column(String(100), nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, SUPERSEDED, CONTRADICTED
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    relationship = sa_relationship("Relationship", back_populates="versions")
    chapter = sa_relationship("Chapter", back_populates="relationship_versions")
    chapter_version = sa_relationship("ChapterVersion", back_populates="relationship_versions")
    extraction_run = sa_relationship("ExtractionRun", back_populates="relationship_versions")
