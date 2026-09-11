from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.world import WorldCreate, WorldUpdate, WorldResponse, WorldStats
from app.services.world_state_service import WorldStateService

router = APIRouter()

@router.post("", response_model=WorldResponse, status_code=status.HTTP_201_CREATED)
def create_world(
    world_in: WorldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    service = WorldStateService(db)
    user_id = current_user.id if current_user else None
    world = service.create_world(name=world_in.name, description=world_in.description or "", user_id=user_id)
    stats = service.get_world_stats(world.id)
    return WorldResponse(
        id=world.id,
        user_id=world.user_id,
        name=world.name,
        description=world.description,
        created_at=world.created_at,
        updated_at=world.updated_at,
        stats=WorldStats(**stats)
    )

@router.get("", response_model=List[WorldResponse])
def list_worlds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    service = WorldStateService(db)
    user_id = current_user.id if current_user else None
    worlds = service.list_worlds(user_id=user_id)
    results = []
    for w in worlds:
        stats = service.get_world_stats(w.id)
        results.append(WorldResponse(
            id=w.id,
            user_id=w.user_id,
            name=w.name,
            description=w.description,
            created_at=w.created_at,
            updated_at=w.updated_at,
            stats=WorldStats(**stats)
        ))
    return results

@router.get("/{world_id}", response_model=WorldResponse)
def get_world(world_id: str, db: Session = Depends(get_db)):
    service = WorldStateService(db)
    world = service.get_world(world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    stats = service.get_world_stats(world.id)
    return WorldResponse(
        id=world.id,
        user_id=world.user_id,
        name=world.name,
        description=world.description,
        created_at=world.created_at,
        updated_at=world.updated_at,
        stats=WorldStats(**stats)
    )

@router.put("/{world_id}", response_model=WorldResponse)
def update_world(world_id: str, world_in: WorldUpdate, db: Session = Depends(get_db)):
    service = WorldStateService(db)
    world = service.get_world(world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    if world_in.name is not None:
        world.name = world_in.name
    if world_in.description is not None:
        world.description = world_in.description
    db.commit()
    db.refresh(world)
    stats = service.get_world_stats(world.id)
    return WorldResponse(
        id=world.id,
        user_id=world.user_id,
        name=world.name,
        description=world.description,
        created_at=world.created_at,
        updated_at=world.updated_at,
        stats=WorldStats(**stats)
    )

@router.delete("/{world_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_world(world_id: str, db: Session = Depends(get_db)):
    service = WorldStateService(db)
    deleted = service.delete_world(world_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    return None
