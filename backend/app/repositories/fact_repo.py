from typing import List, Optional, Any
from sqlalchemy.orm import Session
from app.models.fact import Fact, FactVersion, FactMention
from app.core.constants import FactStatus
from app.repositories.base import BaseRepository

class FactRepository(BaseRepository[Fact]):
    def __init__(self, db: Session):
        super().__init__(Fact, db)

    def get_or_create_fact(self, entity_id: str, property_name: str) -> Fact:
        fact = self.db.query(Fact).filter(
            Fact.entity_id == entity_id,
            Fact.property_name == property_name
        ).first()
        if not fact:
            fact = Fact(entity_id=entity_id, property_name=property_name)
            self.db.add(fact)
            self.db.commit()
            self.db.refresh(fact)
        return fact

    def get_active_version(self, fact_id: str) -> Optional[FactVersion]:
        return self.db.query(FactVersion).filter(
            FactVersion.fact_id == fact_id,
            FactVersion.status == FactStatus.ACTIVE.value
        ).order_by(FactVersion.created_at.desc()).first()

    def add_version(
        self,
        fact_id: str,
        value: Any,
        chapter_id: Optional[str] = None,
        chapter_version_id: Optional[str] = None,
        extraction_run_id: Optional[str] = None,
        status: str = FactStatus.ACTIVE.value,
        confidence: float = 1.0
    ) -> FactVersion:
        version = FactVersion(
            fact_id=fact_id,
            chapter_id=chapter_id,
            chapter_version_id=chapter_version_id,
            extraction_run_id=extraction_run_id,
            value=value,
            status=status,
            confidence=confidence
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def add_mention(
        self,
        entity_id: str,
        property_name: str,
        value: Any,
        extraction_run_id: Optional[str] = None,
        start_position: Optional[int] = None,
        end_position: Optional[int] = None,
        confidence: float = 1.0
    ) -> FactMention:
        mention = FactMention(
            entity_id=entity_id,
            property_name=property_name,
            value=value,
            extraction_run_id=extraction_run_id,
            start_position=start_position,
            end_position=end_position,
            confidence=confidence
        )
        self.db.add(mention)
        self.db.commit()
        self.db.refresh(mention)
        return mention

    def list_by_entity(self, entity_id: str) -> List[Fact]:
        return self.db.query(Fact).filter(Fact.entity_id == entity_id).all()
