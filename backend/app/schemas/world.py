from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class WorldBase(BaseModel):
    name: str
    description: Optional[str] = ""

class WorldCreate(WorldBase):
    pass

class WorldUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WorldStats(BaseModel):
    entities_count: int = 0
    characters_count: int = 0
    locations_count: int = 0
    objects_count: int = 0
    relationships_count: int = 0
    events_count: int = 0
    contradictions_count: int = 0

class WorldResponse(WorldBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    stats: Optional[WorldStats] = None

class WorldDetailResponse(WorldResponse):
    pass
