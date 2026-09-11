from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.hashing import generate_uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    worlds = relationship("World", back_populates="user", cascade="all, delete-orphan")
    extraction_runs = relationship("ExtractionRun", back_populates="creator")
