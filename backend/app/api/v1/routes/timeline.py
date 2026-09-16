from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_world
from app.models.world import World
from app.schemas.timeline import TimelineResponse
from app.services.timeline_service import TimelineService

router = APIRouter()

@router.get("/{world_id}/timeline", response_model=TimelineResponse)
def get_world_timeline(
    world_id: str,
    world: World = Depends(get_current_user_world),
    db: Session = Depends(get_db)
):
    service = TimelineService(db)
    return service.get_world_timeline(world.id)
