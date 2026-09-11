from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Manuscript(Base):
    __tablename__ = "manuscripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    original_file_path = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    world = relationship("World", back_populates="manuscripts")
    chapters = relationship("Chapter", back_populates="manuscript", cascade="all, delete-orphan", order_by="Chapter.chapter_number")
    processing_jobs = relationship("ProcessingJob", back_populates="manuscript", cascade="all, delete-orphan")
