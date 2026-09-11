from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.manuscript import ManuscriptResponse, ManuscriptDetailResponse
from app.schemas.chapter import ChapterResponse
from app.services.manuscript_service import ManuscriptService
from app.workers.tasks.extraction_task import execute_chapter_extraction

router = APIRouter()

@router.post("/{world_id}/manuscripts", status_code=status.HTTP_202_ACCEPTED)
async def upload_manuscript(
    world_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    service = ManuscriptService(db)
    content = await file.read()
    user_id = current_user.id if current_user else None

    result = service.upload_manuscript(
        world_id=world_id,
        filename=file.filename or "manuscript.txt",
        file_bytes=content,
        file_type=file.content_type or "text/plain",
        user_id=user_id
    )

    # Queue extraction runs via BackgroundTasks or Celery
    for run_id, ch_text, ch_id, ch_ver_id in result["extraction_runs"]:
        background_tasks.add_task(
            execute_chapter_extraction,
            world_id=world_id,
            job_id=result["job_id"],
            extraction_run_id=run_id,
            chapter_id=ch_id,
            chapter_version_id=ch_ver_id,
            chapter_text=ch_text
        )

    return {
        "job_id": result["job_id"],
        "manuscript_id": result["manuscript_id"],
        "chapters_total": result["chapters_count"],
        "message": "Manuscript accepted for processing"
    }

@router.get("/{world_id}/manuscripts", response_model=List[ManuscriptResponse])
def list_manuscripts(world_id: str, db: Session = Depends(get_db)):
    service = ManuscriptService(db)
    manuscripts = service.list_manuscripts(world_id)
    return [
        ManuscriptResponse(
            id=m.id,
            world_id=m.world_id,
            title=m.title,
            original_file_path=m.original_file_path,
            file_type=m.file_type,
            chapter_count=len(m.chapters),
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in manuscripts
    ]

@router.get("/{world_id}/manuscripts/{manuscript_id}", response_model=ManuscriptDetailResponse)
def get_manuscript(world_id: str, manuscript_id: str, db: Session = Depends(get_db)):
    service = ManuscriptService(db)
    manuscript = service.get_manuscript(manuscript_id)
    if not manuscript or manuscript.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscript not found")

    chapters = [
        ChapterResponse(
            id=ch.id,
            manuscript_id=ch.manuscript_id,
            chapter_number=ch.chapter_number,
            title=ch.title,
            created_at=ch.created_at,
            updated_at=ch.updated_at
        )
        for ch in manuscript.chapters
    ]

    return ManuscriptDetailResponse(
        id=manuscript.id,
        world_id=manuscript.world_id,
        title=manuscript.title,
        original_file_path=manuscript.original_file_path,
        file_type=manuscript.file_type,
        chapter_count=len(chapters),
        created_at=manuscript.created_at,
        updated_at=manuscript.updated_at,
        chapters=chapters
    )
