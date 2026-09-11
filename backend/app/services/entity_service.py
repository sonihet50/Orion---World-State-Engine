from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.fact import Fact, FactVersion
from app.repositories.entity_repo import EntityRepository
from app.repositories.fact_repo import FactRepository

class EntityService:
    def __init__(self, db: Session):
        self.db = db
        self.entity_repo = EntityRepository(db)
        self.fact_repo = FactRepository(db)

    def list_entities(self, world_id: str, entity_type: Optional[str] = None) -> List[Entity]:
        return self.entity_repo.list_by_world(world_id, entity_type)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entity_repo.get_entity_with_facts(entity_id)

    def create_entity(
        self,
        world_id: str,
        canonical_name: str,
        entity_type: str = "character",
        aliases: List[str] = [],
        attributes: Dict[str, Any] = {}
    ) -> Entity:
        entity = self.entity_repo.create({
            "world_id": world_id,
            "canonical_name": canonical_name.strip(),
            "entity_type": entity_type.lower()
        })

        for alias in aliases:
            if alias.strip():
                self.entity_repo.add_alias(entity.id, alias.strip())

        for prop_name, val in attributes.items():
            fact = self.fact_repo.get_or_create_fact(entity.id, prop_name)
            self.fact_repo.add_version(fact.id, value=val)

        return self.get_entity(entity.id) or entity

    def update_entity(
        self,
        entity_id: str,
        canonical_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[Entity]:
        entity = self.entity_repo.get(entity_id)
        if not entity:
            return None

        update_data = {}
        if canonical_name is not None:
            update_data["canonical_name"] = canonical_name.strip()
        if entity_type is not None:
            update_data["entity_type"] = entity_type.lower()

        if update_data:
            self.entity_repo.update(entity, update_data)

        if attributes:
            for prop_name, val in attributes.items():
                fact = self.fact_repo.get_or_create_fact(entity.id, prop_name)
                self.fact_repo.add_version(fact.id, value=val)

        return self.get_entity(entity_id)

    def delete_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entity_repo.delete(entity_id)

    def add_fact(
        self,
        entity_id: str,
        property_name: str,
        value: Any,
        confidence: float = 1.0
    ) -> FactVersion:
        fact = self.fact_repo.get_or_create_fact(entity_id, property_name)
        return self.fact_repo.add_version(
            fact_id=fact.id,
            value=value,
            confidence=confidence
        )

    def delete_fact(self, fact_id: str) -> bool:
        fact = self.fact_repo.get(fact_id)
        if fact:
            self.db.delete(fact)
            self.db.commit()
            return True
        return False
