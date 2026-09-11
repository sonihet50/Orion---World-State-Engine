from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    manuscript_id = Column(String(36), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False, default=1)
    title = Column(String(255), nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    manuscript = relationship("Manuscript", back_populates="chapters")
    versions = relationship("ChapterVersion", back_populates="chapter", cascade="all, delete-orphan", order_by="ChapterVersion.version_number")
    fact_versions = relationship("FactVersion", back_populates="chapter")
    relationship_versions = relationship("RelationshipVersion", back_populates="chapter")
    events = relationship("Event", back_populates="chapter")
