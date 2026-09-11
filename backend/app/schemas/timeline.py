from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class TimelineParticipant(BaseModel):
    entity_id: str
    entity_name: Optional[str] = None
    role: str

class TimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    world_id: str
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    event_type: str
    description: str
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    confidence: float
    created_at: datetime
    participants: List[TimelineParticipant] = []

class TimelineResponse(BaseModel):
    events: List[TimelineEventResponse] = []
    total: int = 0
