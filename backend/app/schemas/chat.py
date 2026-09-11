from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ChatCitation(BaseModel):
    source_type: str  # entity, fact, event, relationship
    source_id: str
    title: str
    snippet: str

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str

class ChatQueryRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    entity_focus: Optional[str] = None
    timeline_event_focus: Optional[str] = None

class ChatQueryResponse(BaseModel):
    response: str
    citations: List[ChatCitation] = []
    suggested_actions: List[str] = []
