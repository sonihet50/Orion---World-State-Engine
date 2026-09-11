from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class ChapterVersion(Base):
    __tablename__ = "chapter_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    content_path = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chapter = relationship("Chapter", back_populates="versions")
    extraction_runs = relationship("ExtractionRun", back_populates="chapter_version", cascade="all, delete-orphan")
    fact_versions = relationship("FactVersion", back_populates="chapter_version")
    relationship_versions = relationship("RelationshipVersion", back_populates="chapter_version")
    events = relationship("Event", back_populates="chapter_version")
