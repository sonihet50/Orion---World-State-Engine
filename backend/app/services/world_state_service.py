import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.world import World
from app.models.entity import Entity
from app.models.fact import Fact, FactVersion
from app.models.relationship import Relationship, RelationshipVersion
from app.models.event import Event, EventParticipant
from app.repositories.world_repo import WorldRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.fact_repo import FactRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.repositories.event_repo import EventRepository
from app.repositories.contradiction_repo import ContradictionRepository
from app.pipeline.resolution.fact_resolution import resolve_fact_update
from app.pipeline.resolution.relationship_resolution import resolve_relationship_update
from app.services.consistency_service import ConsistencyService
from app.config.logging import get_logger

logger = get_logger(__name__)

class WorldStateService:
    def __init__(self, db: Session):
        self.db = db
        self.world_repo = WorldRepository(db)
        self.entity_repo = EntityRepository(db)
        self.fact_repo = FactRepository(db)
        self.relationship_repo = RelationshipRepository(db)
        self.event_repo = EventRepository(db)
        self.contradiction_repo = ContradictionRepository(db)
        self.consistency_service = ConsistencyService(db)

    def create_world(self, name: str, description: str = "", user_id: Optional[str] = None) -> World:
        return self.world_repo.create({
            "name": name,
            "description": description,
            "user_id": user_id
        })

    def get_world(self, world_id: str) -> Optional[World]:
        return self.world_repo.get(world_id)

    def list_worlds(self, user_id: Optional[str] = None) -> List[World]:
        return self.world_repo.list_worlds(user_id=user_id)

    def get_world_stats(self, world_id: str) -> Dict[str, int]:
        return self.world_repo.get_world_stats(world_id)

    def delete_world(self, world_id: str) -> Optional[World]:
        return self.world_repo.delete(world_id)

    def integrate_extraction_result(
        self,
        world_id: str,
        extraction_data: Dict[str, Any],
        chapter_id: Optional[str] = None,
        chapter_version_id: Optional[str] = None,
        extraction_run_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Integrates parsed extraction data into persistent relational state:
        - Resolves or creates Entities
        - Adds Aliases and Mentions
        - Inserts Facts & FactVersions (with consistency check)
        - Inserts Relationships & RelationshipVersions
        - Inserts Events & Participants
        - Detects Contradictions
        """
        counts = {
            "entities_created": 0,
            "entities_updated": 0,
            "facts_added": 0,
            "relationships_added": 0,
            "events_added": 0,
            "contradictions_found": 0
        }

        # Map canonical/mention names to DB Entity objects
        entity_cache: Dict[str, Entity] = {}

        # 1. Process Entities
        for ent_data in extraction_data.get("entities", []):
            canonical = ent_data.get("canonical_name", "").strip()
            if not canonical:
                continue

            # Look up by canonical or alias in world
            existing_ent = self.entity_repo.get_by_canonical(world_id, canonical)
            if not existing_ent:
                for alias in ent_data.get("aliases", []):
                    existing_ent = self.entity_repo.get_by_alias(world_id, alias)
                    if existing_ent:
                        break

            if existing_ent:
                entity = existing_ent
                counts["entities_updated"] += 1
                # Add any new aliases
                for alias in ent_data.get("aliases", []):
                    self.entity_repo.add_alias(entity.id, alias)
            else:
                entity = self.entity_repo.create({
                    "world_id": world_id,
                    "entity_type": ent_data.get("type", "unknown").lower(),
                    "canonical_name": canonical,
                    "provenance": json.dumps(ent_data.get("source_chunk", ""))
                })
                counts["entities_created"] += 1
                for alias in ent_data.get("aliases", []):
                    self.entity_repo.add_alias(entity.id, alias)

            entity_cache[canonical.lower()] = entity
            for alias in ent_data.get("aliases", []):
                entity_cache[alias.lower()] = entity

            # Record mention
            mention_text = ent_data.get("mention") or canonical
            self.entity_repo.add_mention(
                entity_id=entity.id,
                surface_text=mention_text,
                extraction_run_id=extraction_run_id
            )

            # Insert Facts & Version Check
            attributes = ent_data.get("attributes", {})
            if isinstance(attributes, dict):
                for prop_name, new_val in attributes.items():
                    if new_val is None or new_val == "":
                        continue

                    fact = self.fact_repo.get_or_create_fact(entity.id, prop_name)
                    active_ver = self.fact_repo.get_active_version(fact.id)

                    old_val = active_ver.value if active_ver else None
                    status, contradiction_info = resolve_fact_update(
                        property_name=prop_name,
                        old_value=old_val,
                        new_value=new_val,
                        entity_name=entity.canonical_name
                    )

                    new_version = self.fact_repo.add_version(
                        fact_id=fact.id,
                        value=new_val,
                        chapter_id=chapter_id,
                        chapter_version_id=chapter_version_id,
                        extraction_run_id=extraction_run_id,
                        status=status,
                        confidence=1.0
                    )
                    counts["facts_added"] += 1

                    if contradiction_info and active_ver:
                        # Record contradiction
                        self.contradiction_repo.create_contradiction(
                            world_id=world_id,
                            contradiction_type=contradiction_info["contradiction_type"],
                            old_fact_version_id=active_ver.id,
                            new_fact_version_id=new_version.id,
                            explanation=contradiction_info["explanation"],
                            confidence=0.9
                        )
                        counts["contradictions_found"] += 1

        # Helper for entity resolution from cache or DB
        def resolve_cached_entity(name_str: str) -> Optional[Entity]:
            norm = name_str.strip().lower()
            if norm in entity_cache:
                return entity_cache[norm]
            ent = self.entity_repo.get_by_canonical(world_id, name_str)
            if not ent:
                ent = self.entity_repo.get_by_alias(world_id, name_str)
            if ent:
                entity_cache[norm] = ent
            return ent

        # 2. Process Relationships
        for rel_data in extraction_data.get("relationships", []):
            subj_name = rel_data.get("subject", "")
            obj_name = rel_data.get("object", "")
            rel_type = rel_data.get("predicate", "RELATED_TO")

            subj_ent = resolve_cached_entity(subj_name)
            obj_ent = resolve_cached_entity(obj_name)

            if subj_ent and obj_ent and subj_ent.id != obj_ent.id:
                rel = self.relationship_repo.get_or_create_relationship(
                    world_id=world_id,
                    source_entity_id=subj_ent.id,
                    target_entity_id=obj_ent.id
                )

                active_ver = self.relationship_repo.get_active_version(rel.id)
                old_type = active_ver.relationship_type if active_ver else ""

                status, contradiction_info = resolve_relationship_update(
                    old_type=old_type,
                    new_type=rel_type,
                    subj_name=subj_ent.canonical_name,
                    obj_name=obj_ent.canonical_name
                )

                new_ver = self.relationship_repo.add_version(
                    relationship_id=rel.id,
                    relationship_type=rel_type,
                    chapter_id=chapter_id,
                    chapter_version_id=chapter_version_id,
                    extraction_run_id=extraction_run_id,
                    status=status,
                    confidence=1.0
                )
                counts["relationships_added"] += 1

                if contradiction_info and active_ver:
                    self.contradiction_repo.create_contradiction(
                        world_id=world_id,
                        contradiction_type=contradiction_info["contradiction_type"],
                        old_relationship_version_id=active_ver.id,
                        new_relationship_version_id=new_ver.id,
                        explanation=contradiction_info["explanation"],
                        confidence=0.85
                    )
                    counts["contradictions_found"] += 1

        # 3. Process Events
        for ev_data in extraction_data.get("events", []):
            desc = ev_data.get("evidence") or ev_data.get("description") or f"Event ({ev_data.get('type')})"
            ev = self.event_repo.create_event(
                world_id=world_id,
                description=desc,
                event_type=ev_data.get("type", "EVENT"),
                chapter_id=chapter_id,
                chapter_version_id=chapter_version_id,
                extraction_run_id=extraction_run_id,
                confidence=1.0
            )
            counts["events_added"] += 1

            for p_name in ev_data.get("participants", []):
                p_ent = resolve_cached_entity(p_name)
                if p_ent:
                    self.event_repo.add_participant(ev.id, p_ent.id, role="PARTICIPANT")

        # 4. Consistency Checks (Temporal & Cycles)
        detected_cons = self.consistency_service.run_checks(
            world_id=world_id,
            events=extraction_data.get("events", []),
            temporal_relations=extraction_data.get("temporal_relations", [])
        )
        counts["contradictions_found"] += len(detected_cons)

        self.db.commit()
        return counts
