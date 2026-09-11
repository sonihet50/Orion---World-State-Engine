from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.manuscript import Manuscript
from app.repositories.base import BaseRepository

class ManuscriptRepository(BaseRepository[Manuscript]):
    def __init__(self, db: Session):
        super().__init__(Manuscript, db)

    def get_by_world(self, world_id: str) -> List[Manuscript]:
        return self.db.query(Manuscript).filter(
            Manuscript.world_id == world_id
        ).order_by(Manuscript.created_at.desc()).all()

    def get_with_chapters(self, manuscript_id: str) -> Optional[Manuscript]:
        return self.db.query(Manuscript).options(
            joinedload(Manuscript.chapters)
        ).filter(Manuscript.id == manuscript_id).first()
