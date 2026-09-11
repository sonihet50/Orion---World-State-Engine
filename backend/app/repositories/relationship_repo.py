from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.relationship import Relationship, RelationshipVersion
from app.core.constants import RelationshipStatus
from app.repositories.base import BaseRepository

class RelationshipRepository(BaseRepository[Relationship]):
    def __init__(self, db: Session):
        super().__init__(Relationship, db)

    def get_or_create_relationship(
        self,
        world_id: str,
        source_entity_id: str,
        target_entity_id: str,
        source_extraction_id: Optional[str] = None
    ) -> Relationship:
        rel = self.db.query(Relationship).filter(
            Relationship.world_id == world_id,
            Relationship.source_entity_id == source_entity_id,
            Relationship.target_entity_id == target_entity_id
        ).first()
        if not rel:
            rel = Relationship(
                world_id=world_id,
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                source_extraction_id=source_extraction_id
            )
            self.db.add(rel)
            self.db.commit()
            self.db.refresh(rel)
        return rel

    def get_active_version(self, relationship_id: str) -> Optional[RelationshipVersion]:
        return self.db.query(RelationshipVersion).filter(
            RelationshipVersion.relationship_id == relationship_id,
            RelationshipVersion.status == RelationshipStatus.ACTIVE.value
        ).order_by(RelationshipVersion.created_at.desc()).first()

    def add_version(
        self,
        relationship_id: str,
        relationship_type: str,
        chapter_id: Optional[str] = None,
        chapter_version_id: Optional[str] = None,
        extraction_run_id: Optional[str] = None,
        status: str = RelationshipStatus.ACTIVE.value,
        confidence: float = 1.0
    ) -> RelationshipVersion:
        version = RelationshipVersion(
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            chapter_id=chapter_id,
            chapter_version_id=chapter_version_id,
            extraction_run_id=extraction_run_id,
            status=status,
            confidence=confidence
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_by_world(self, world_id: str) -> List[Relationship]:
        return self.db.query(Relationship).options(
            joinedload(Relationship.versions),
            joinedload(Relationship.source_entity),
            joinedload(Relationship.target_entity)
        ).filter(Relationship.world_id == world_id).all()

    def list_by_entity(self, entity_id: str) -> List[Relationship]:
        return self.db.query(Relationship).options(
            joinedload(Relationship.versions),
            joinedload(Relationship.source_entity),
            joinedload(Relationship.target_entity)
        ).filter(
            (Relationship.source_entity_id == entity_id) |
            (Relationship.target_entity_id == entity_id)
        ).all()
