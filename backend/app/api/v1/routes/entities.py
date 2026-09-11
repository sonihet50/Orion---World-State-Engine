from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.entity import (
    EntityCreate, EntityUpdate, EntityResponse, EntityDetailResponse,
    FactCreate, FactResponse, FactVersionResponse
)
from app.services.entity_service import EntityService

router = APIRouter()

@router.get("/{world_id}/entities", response_model=List[EntityResponse])
def list_entities(
    world_id: str,
    entity_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = EntityService(db)
    entities = service.list_entities(world_id, entity_type)

    results = []
    for ent in entities:
        aliases = [a.alias for a in ent.aliases]
        facts_out = []
        for f in ent.facts:
            active_v = f.versions[0] if f.versions else None
            v_resp = None
            if active_v:
                v_resp = FactVersionResponse(
                    id=active_v.id,
                    fact_id=active_v.fact_id,
                    chapter_id=active_v.chapter_id,
                    value=active_v.value,
                    status=active_v.status,
                    confidence=active_v.confidence,
                    created_at=active_v.created_at
                )
            facts_out.append(FactResponse(
                id=f.id,
                property_name=f.property_name,
                created_at=f.created_at,
                current_version=v_resp
            ))

        results.append(EntityResponse(
            id=ent.id,
            world_id=ent.world_id,
            entity_type=ent.entity_type,
            canonical_name=ent.canonical_name,
            source_extraction_id=ent.source_extraction_id,
            provenance=ent.provenance,
            aliases=aliases,
            facts=facts_out,
            created_at=ent.created_at,
            updated_at=ent.updated_at
        ))
    return results

@router.post("/{world_id}/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(world_id: str, ent_in: EntityCreate, db: Session = Depends(get_db)):
    service = EntityService(db)
    ent = service.create_entity(
        world_id=world_id,
        canonical_name=ent_in.canonical_name,
        entity_type=ent_in.entity_type,
        aliases=ent_in.aliases,
        attributes=ent_in.attributes
    )
    return EntityResponse(
        id=ent.id,
        world_id=ent.world_id,
        entity_type=ent.entity_type,
        canonical_name=ent.canonical_name,
        aliases=[a.alias for a in ent.aliases],
        facts=[],
        created_at=ent.created_at,
        updated_at=ent.updated_at
    )

@router.get("/{world_id}/entities/{entity_id}", response_model=EntityDetailResponse)
def get_entity(world_id: str, entity_id: str, db: Session = Depends(get_db)):
    service = EntityService(db)
    ent = service.get_entity(entity_id)
    if not ent or ent.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

    aliases = [a.alias for a in ent.aliases]
    facts_out = []
    for f in ent.facts:
        active_v = f.versions[0] if f.versions else None
        v_resp = None
        if active_v:
            v_resp = FactVersionResponse(
                id=active_v.id,
                fact_id=active_v.fact_id,
                chapter_id=active_v.chapter_id,
                value=active_v.value,
                status=active_v.status,
                confidence=active_v.confidence,
                created_at=active_v.created_at
            )
        facts_out.append(FactResponse(
            id=f.id,
            property_name=f.property_name,
            created_at=f.created_at,
            current_version=v_resp
        ))

    rels_out = []
    for r in ent.outgoing_relationships:
        latest = r.versions[0] if r.versions else None
        rels_out.append({
            "id": r.id,
            "target_id": r.target_entity_id,
            "target_name": r.target_entity.canonical_name if r.target_entity else "Unknown",
            "type": latest.relationship_type if latest else "RELATED_TO"
        })

    events_out = [
        {"id": ep.event.id, "type": ep.event.event_type, "role": ep.role, "description": ep.event.description}
        for ep in ent.event_participants if ep.event
    ]

    return EntityDetailResponse(
        id=ent.id,
        world_id=ent.world_id,
        entity_type=ent.entity_type,
        canonical_name=ent.canonical_name,
        source_extraction_id=ent.source_extraction_id,
        provenance=ent.provenance,
        aliases=aliases,
        facts=facts_out,
        created_at=ent.created_at,
        updated_at=ent.updated_at,
        relationships=rels_out,
        events=events_out
    )

@router.put("/{world_id}/entities/{entity_id}", response_model=EntityResponse)
def update_entity(world_id: str, entity_id: str, ent_in: EntityUpdate, db: Session = Depends(get_db)):
    service = EntityService(db)
    ent = service.update_entity(
        entity_id=entity_id,
        canonical_name=ent_in.canonical_name,
        entity_type=ent_in.entity_type,
        attributes=ent_in.attributes
    )
    if not ent or ent.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

    return EntityResponse(
        id=ent.id,
        world_id=ent.world_id,
        entity_type=ent.entity_type,
        canonical_name=ent.canonical_name,
        aliases=[a.alias for a in ent.aliases],
        facts=[],
        created_at=ent.created_at,
        updated_at=ent.updated_at
    )

@router.delete("/{world_id}/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(world_id: str, entity_id: str, db: Session = Depends(get_db)):
    service = EntityService(db)
    deleted = service.delete_entity(entity_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return None

@router.post("/{world_id}/entities/{entity_id}/facts", status_code=status.HTTP_201_CREATED)
def add_fact_to_entity(world_id: str, entity_id: str, fact_in: FactCreate, db: Session = Depends(get_db)):
    service = EntityService(db)
    ent = service.get_entity(entity_id)
    if not ent or ent.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    fact_ver = service.add_fact(
        entity_id=entity_id,
        property_name=fact_in.property_name,
        value=fact_in.value,
        confidence=fact_in.confidence
    )
    return {"id": fact_ver.id, "property": fact_in.property_name, "value": fact_ver.value, "status": fact_ver.status}

@router.delete("/{world_id}/entities/{entity_id}/facts/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fact(world_id: str, entity_id: str, fact_id: str, db: Session = Depends(get_db)):
    service = EntityService(db)
    if not service.delete_fact(fact_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fact not found")
    return None
