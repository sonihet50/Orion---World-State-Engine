from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class World(Base):
    __tablename__ = "worlds"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="worlds")
    manuscripts = relationship("Manuscript", back_populates="world", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="world", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="world", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="world", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="world", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="world", cascade="all, delete-orphan")
