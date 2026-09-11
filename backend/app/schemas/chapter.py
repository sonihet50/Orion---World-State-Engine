from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChapterVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chapter_id: str
    version_number: int
    is_current: bool
    content_path: Optional[str] = None
    content_hash: Optional[str] = None
    created_at: datetime

class ChapterBase(BaseModel):
    chapter_number: int
    title: str

class ChapterCreate(ChapterBase):
    content: Optional[str] = None

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ChapterResponse(ChapterBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    manuscript_id: str
    created_at: datetime
    updated_at: datetime
    latest_version: Optional[ChapterVersionResponse] = None
    content: Optional[str] = None
