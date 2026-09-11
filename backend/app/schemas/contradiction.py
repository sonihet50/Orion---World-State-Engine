from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class ContradictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    world_id: str
    contradiction_type: str
    explanation: str
    confidence: float
    status: str
    old_fact_version_id: Optional[str] = None
    new_fact_version_id: Optional[str] = None
    old_relationship_version_id: Optional[str] = None
    new_relationship_version_id: Optional[str] = None
    event_id_a: Optional[str] = None
    event_id_b: Optional[str] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class ContradictionResolveRequest(BaseModel):
    status: str = "RESOLVED"
    resolution_notes: Optional[str] = None
    preferred_fact_version_id: Optional[str] = None
