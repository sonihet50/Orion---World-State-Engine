from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_world
from app.models.world import World
from app.schemas.graph import GraphResponse
from app.services.graph_service import GraphService

router = APIRouter()

@router.get("/{world_id}/graph", response_model=GraphResponse)
def get_world_graph(
    world_id: str,
    world: World = Depends(get_current_user_world),
    db: Session = Depends(get_db)
):
    service = GraphService(db)
    return service.get_world_graph(world.id)
