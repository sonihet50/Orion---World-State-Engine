from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id", ondelete="SET NULL"), nullable=True)
    extraction_run_id = Column(String(36), ForeignKey("extraction_runs.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(100), default="EVENT", nullable=False)
    description = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    world = relationship("World", back_populates="events")
    chapter = relationship("Chapter", back_populates="events")
    chapter_version = relationship("ChapterVersion", back_populates="events")
    extraction_run = relationship("ExtractionRun", back_populates="events")
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")


class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), default="PARTICIPANT", nullable=False)

    event = relationship("Event", back_populates="participants")
    entity = relationship("Entity", back_populates="event_participants")
