from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.chapter import ChapterResponse

class ManuscriptBase(BaseModel):
    title: str

class ManuscriptCreate(ManuscriptBase):
    pass

class ManuscriptResponse(ManuscriptBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    world_id: str
    original_file_path: Optional[str] = None
    file_type: Optional[str] = None
    chapter_count: int = 0
    created_at: datetime
    updated_at: datetime

class ManuscriptDetailResponse(ManuscriptResponse):
    chapters: List[ChapterResponse] = []
