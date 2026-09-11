from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chapter import Chapter
from app.models.chapter_version import ChapterVersion
from app.repositories.base import BaseRepository

class ChapterRepository(BaseRepository[Chapter]):
    def __init__(self, db: Session):
        super().__init__(Chapter, db)

    def get_by_manuscript(self, manuscript_id: str) -> List[Chapter]:
        return self.db.query(Chapter).filter(
            Chapter.manuscript_id == manuscript_id
        ).order_by(Chapter.chapter_number.asc()).all()

    def get_latest_version(self, chapter_id: str) -> Optional[ChapterVersion]:
        return self.db.query(ChapterVersion).filter(
            ChapterVersion.chapter_id == chapter_id,
            ChapterVersion.is_current == True
        ).first()

    def create_version(
        self,
        chapter_id: str,
        content_path: Optional[str] = None,
        content_hash: Optional[str] = None,
        version_number: Optional[int] = None
    ) -> ChapterVersion:
        # Mark previous versions as not current
        self.db.query(ChapterVersion).filter(
            ChapterVersion.chapter_id == chapter_id
        ).update({"is_current": False})

        if version_number is None:
            max_v = self.db.query(ChapterVersion).filter(
                ChapterVersion.chapter_id == chapter_id
            ).count()
            version_number = max_v + 1

        new_version = ChapterVersion(
            chapter_id=chapter_id,
            version_number=version_number,
            is_current=True,
            content_path=content_path,
            content_hash=content_hash
        )
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        return new_version
