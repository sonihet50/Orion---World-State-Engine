from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    contradiction_type = Column(String(50), nullable=False)
    old_fact_version_id = Column(String(36), ForeignKey("fact_versions.id", ondelete="SET NULL"), nullable=True)
    new_fact_version_id = Column(String(36), ForeignKey("fact_versions.id", ondelete="SET NULL"), nullable=True)
    old_relationship_version_id = Column(String(36), ForeignKey("relationship_versions.id", ondelete="SET NULL"), nullable=True)
    new_relationship_version_id = Column(String(36), ForeignKey("relationship_versions.id", ondelete="SET NULL"), nullable=True)
    event_id_a = Column(String(36), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    event_id_b = Column(String(36), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    explanation = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    status = Column(String(50), default="DETECTED", nullable=False)  # DETECTED, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    world = relationship("World", back_populates="contradictions")
    old_fact_version = relationship("FactVersion", foreign_keys=[old_fact_version_id])
    new_fact_version = relationship("FactVersion", foreign_keys=[new_fact_version_id])
    old_relationship_version = relationship("RelationshipVersion", foreign_keys=[old_relationship_version_id])
    new_relationship_version = relationship("RelationshipVersion", foreign_keys=[new_relationship_version_id])
    event_a = relationship("Event", foreign_keys=[event_id_a])
    event_b = relationship("Event", foreign_keys=[event_id_b])
