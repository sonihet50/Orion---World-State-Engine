from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.chapter import ChapterResponse, ChapterUpdate, ChapterVersionResponse
from app.services.chapter_service import ChapterService
from app.workers.tasks.extraction_task import execute_chapter_extraction

router = APIRouter()

@router.get("/{world_id}/manuscripts/{manuscript_id}/chapters", response_model=List[ChapterResponse])
def list_chapters(world_id: str, manuscript_id: str, db: Session = Depends(get_db)):
    service = ChapterService(db)
    chapters = service.list_chapters(manuscript_id)
    return [
        ChapterResponse(
            id=ch.id,
            manuscript_id=ch.manuscript_id,
            chapter_number=ch.chapter_number,
            title=ch.title,
            created_at=ch.created_at,
            updated_at=ch.updated_at
        )
        for ch in chapters
    ]

@router.get("/{world_id}/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(world_id: str, chapter_id: str, db: Session = Depends(get_db)):
    service = ChapterService(db)
    chapter = service.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    content = service.get_chapter_content(chapter_id)
    latest_ver = chapter.versions[0] if chapter.versions else None
    latest_resp = None
    if latest_ver:
        latest_resp = ChapterVersionResponse(
            id=latest_ver.id,
            chapter_id=latest_ver.chapter_id,
            version_number=latest_ver.version_number,
            is_current=latest_ver.is_current,
            content_path=latest_ver.content_path,
            content_hash=latest_ver.content_hash,
            created_at=latest_ver.created_at
        )

    return ChapterResponse(
        id=chapter.id,
        manuscript_id=chapter.manuscript_id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
        latest_version=latest_resp,
        content=content
    )

@router.put("/{world_id}/chapters/{chapter_id}", status_code=status.HTTP_202_ACCEPTED)
def update_chapter_content(
    world_id: str,
    chapter_id: str,
    chapter_in: ChapterUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    service = ChapterService(db)
    chapter = service.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    if chapter_in.title:
        chapter.title = chapter_in.title
        db.commit()

    if chapter_in.content is not None:
        user_id = current_user.id if current_user else None
        version, job, run = service.update_chapter_content(
            chapter_id=chapter_id,
            content_text=chapter_in.content,
            user_id=user_id
        )

        background_tasks.add_task(
            execute_chapter_extraction,
            world_id=world_id,
            job_id=job.id,
            extraction_run_id=run.id,
            chapter_id=chapter.id,
            chapter_version_id=version.id,
            chapter_text=chapter_in.content,
            chapter_number=chapter.chapter_number
        )

        return {
            "chapter_id": chapter.id,
            "version_id": version.id,
            "job_id": job.id,
            "status": "re_extraction_queued"
        }

    return {"chapter_id": chapter.id, "message": "Chapter updated"}
