from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import ChatService
from app.services.world_state_service import WorldStateService

router = APIRouter()

@router.post("/{world_id}/chat", response_model=ChatQueryResponse)
def chat_with_world(
    world_id: str,
    query_in: ChatQueryRequest,
    db: Session = Depends(get_db)
):
    ws_service = WorldStateService(db)
    world = ws_service.get_world(world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    chat_service = ChatService(db)
    response = chat_service.query(
        world_id=world_id,
        message=query_in.message,
        history=query_in.history,
        entity_focus=query_in.entity_focus,
        timeline_event_focus=query_in.timeline_event_focus
    )
    return response
