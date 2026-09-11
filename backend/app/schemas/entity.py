from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AliasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alias: str
    confidence: float

class FactVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fact_id: str
    chapter_id: Optional[str] = None
    value: Any = None
    status: str
    confidence: float
    created_at: datetime

class FactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    property_name: str
    created_at: datetime
    current_version: Optional[FactVersionResponse] = None

class FactCreate(BaseModel):
    property_name: str
    value: Any
    confidence: float = 1.0

class EntityBase(BaseModel):
    entity_type: str = "character"
    canonical_name: str

class EntityCreate(EntityBase):
    aliases: List[str] = []
    attributes: Dict[str, Any] = {}

class EntityUpdate(BaseModel):
    canonical_name: Optional[str] = None
    entity_type: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class EntityResponse(EntityBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    world_id: str
    source_extraction_id: Optional[str] = None
    provenance: Optional[str] = None
    aliases: List[str] = []
    facts: List[FactResponse] = []
    created_at: datetime
    updated_at: datetime

class EntityDetailResponse(EntityResponse):
    relationships: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
