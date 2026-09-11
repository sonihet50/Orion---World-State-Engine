from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.contradiction import ContradictionResponse, ContradictionResolveRequest
from app.services.consistency_service import ConsistencyService

router = APIRouter()

@router.get("/{world_id}/contradictions", response_model=List[ContradictionResponse])
def list_contradictions(
    world_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    service = ConsistencyService(db)
    contradictions = service.list_contradictions(world_id, status=status_filter)
    return contradictions

@router.post("/{world_id}/contradictions/{contradiction_id}/resolve", response_model=ContradictionResponse)
def resolve_contradiction(
    world_id: str,
    contradiction_id: str,
    resolve_in: ContradictionResolveRequest,
    db: Session = Depends(get_db)
):
    service = ConsistencyService(db)
    con = service.resolve_contradiction(
        contradiction_id=contradiction_id,
        status=resolve_in.status,
        preferred_fact_version_id=resolve_in.preferred_fact_version_id
    )
    if not con or con.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contradiction not found")
    return con
