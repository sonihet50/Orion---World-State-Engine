from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id", ondelete="CASCADE"), nullable=False)
    processing_job_id = Column(String(36), ForeignKey("processing_jobs.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    extractor_version = Column(String(100), default="llama3.1:8b", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    chapter_version = relationship("ChapterVersion", back_populates="extraction_runs")
    processing_job = relationship("ProcessingJob", back_populates="extraction_runs")
    creator = relationship("User", back_populates="extraction_runs")
    entity_mentions = relationship("EntityMention", back_populates="extraction_run", cascade="all, delete-orphan")
    fact_mentions = relationship("FactMention", back_populates="extraction_run", cascade="all, delete-orphan")
    fact_versions = relationship("FactVersion", back_populates="extraction_run")
    relationship_versions = relationship("RelationshipVersion", back_populates="extraction_run")
    events = relationship("Event", back_populates="extraction_run")
