from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.contradiction import Contradiction
from app.core.constants import ContradictionStatus
from app.repositories.base import BaseRepository

class ContradictionRepository(BaseRepository[Contradiction]):
    def __init__(self, db: Session):
        super().__init__(Contradiction, db)

    def create_contradiction(
        self,
        world_id: str,
        contradiction_type: str,
        explanation: str,
        old_fact_version_id: Optional[str] = None,
        new_fact_version_id: Optional[str] = None,
        old_relationship_version_id: Optional[str] = None,
        new_relationship_version_id: Optional[str] = None,
        event_id_a: Optional[str] = None,
        event_id_b: Optional[str] = None,
        confidence: float = 1.0,
        status: str = ContradictionStatus.DETECTED.value
    ) -> Contradiction:
        con = Contradiction(
            world_id=world_id,
            contradiction_type=contradiction_type,
            explanation=explanation,
            old_fact_version_id=old_fact_version_id,
            new_fact_version_id=new_fact_version_id,
            old_relationship_version_id=old_relationship_version_id,
            new_relationship_version_id=new_relationship_version_id,
            event_id_a=event_id_a,
            event_id_b=event_id_b,
            confidence=confidence,
            status=status
        )
        self.db.add(con)
        self.db.commit()
        self.db.refresh(con)
        return con

    def list_by_world(self, world_id: str, status: Optional[str] = None) -> List[Contradiction]:
        query = self.db.query(Contradiction).filter(Contradiction.world_id == world_id)
        if status:
            query = query.filter(Contradiction.status == status)
        return query.order_by(Contradiction.created_at.desc()).all()

    def resolve(self, contradiction_id: str, status: str = "RESOLVED") -> Optional[Contradiction]:
        con = self.get(contradiction_id)
        if con:
            con.status = status
            self.db.commit()
            self.db.refresh(con)
        return con
