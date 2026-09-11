from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Fact(Base):
    __tablename__ = "facts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    property_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entity = relationship("Entity", back_populates="facts")
    versions = relationship("FactVersion", back_populates="fact", cascade="all, delete-orphan", order_by="FactVersion.created_at.desc()")


class FactVersion(Base):
    __tablename__ = "fact_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    fact_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id", ondelete="SET NULL"), nullable=True)
    extraction_run_id = Column(String(36), ForeignKey("extraction_runs.id", ondelete="SET NULL"), nullable=True)
    value = Column(JSON, nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, SUPERSEDED, CONTRADICTED
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    fact = relationship("Fact", back_populates="versions")
    chapter = relationship("Chapter", back_populates="fact_versions")
    chapter_version = relationship("ChapterVersion", back_populates="fact_versions")
    extraction_run = relationship("ExtractionRun", back_populates="fact_versions")


class FactMention(Base):
    __tablename__ = "fact_mentions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    extraction_run_id = Column(String(36), ForeignKey("extraction_runs.id", ondelete="SET NULL"), nullable=True)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    property_name = Column(String(255), nullable=False)
    value = Column(JSON, nullable=True)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)

    extraction_run = relationship("ExtractionRun", back_populates="fact_mentions")
