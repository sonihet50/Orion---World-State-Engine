from datetime import datetime
from typing import Dict, Any, Optional
from app.core.database import SessionLocal
from app.models.processing_job import ProcessingJob
from app.models.extraction_run import ExtractionRun
from app.core.constants import JobStatus, ExtractionRunStatus
from app.pipeline.extractor import orchestrator
from app.services.world_state_service import WorldStateService
from app.workers.celery_app import celery_app
from app.config.logging import get_logger

logger = get_logger(__name__)

def execute_chapter_extraction(
    world_id: str,
    job_id: str,
    extraction_run_id: str,
    chapter_id: str,
    chapter_version_id: str,
    chapter_text: str,
    chapter_number: int = 1
) -> Dict[str, Any]:
    """
    Executes end-to-end extraction and integration for one chapter:
    1. Sets ExtractionRun to processing.
    2. Runs LLM extraction orchestrator.
    3. Integrates entities, facts, relationships, events, and contradictions.
    4. Updates ExtractionRun and parent ProcessingJob progress.
    """
    db = SessionLocal()
    try:
        # Mark ExtractionRun as processing
        run = db.query(ExtractionRun).filter(ExtractionRun.id == extraction_run_id).first()
        if run:
            run.status = ExtractionRunStatus.PROCESSING.value
            run.started_at = datetime.utcnow()
            db.commit()

        # Mark parent Job as processing
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job and job.status == JobStatus.QUEUED.value:
            job.status = JobStatus.PROCESSING.value
            job.started_at = datetime.utcnow()
            db.commit()

        # Run extraction
        logger.info(f"Starting extraction for chapter {chapter_number} (run {extraction_run_id})")
        extracted_data = orchestrator.extract_chapter(chapter_text, chapter_number=chapter_number)

        # Integrate into world state
        ws_service = WorldStateService(db)
        counts = ws_service.integrate_extraction_result(
            world_id=world_id,
            extraction_data=extracted_data,
            chapter_id=chapter_id,
            chapter_version_id=chapter_version_id,
            extraction_run_id=extraction_run_id
        )

        # Mark run as DONE
        if run:
            run.status = ExtractionRunStatus.DONE.value
            run.completed_at = datetime.utcnow()
            db.commit()

        # Update parent Job progress
        if job:
            job.chapters_completed += 1
            if job.chapters_completed >= job.chapters_total:
                job.status = JobStatus.DONE.value
                job.completed_at = datetime.utcnow()
            db.commit()

        logger.info(f"Extraction completed for chapter {chapter_number}: {counts}")
        return {"status": "success", "counts": counts}

    except Exception as e:
        logger.error(f"Extraction failed for run {extraction_run_id}: {e}", exc_info=True)
        # Mark run as FAILED
        if run:
            run.status = ExtractionRunStatus.FAILED.value
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()

        # Mark job as FAILED
        if job:
            job.status = JobStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        return {"status": "failed", "error": str(e)}

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.extract_chapter", max_retries=2)
def extract_chapter_task(
    self,
    world_id: str,
    job_id: str,
    extraction_run_id: str,
    chapter_id: str,
    chapter_version_id: str,
    chapter_text: str,
    chapter_number: int = 1
):
    """Celery background task wrapper."""
    return execute_chapter_extraction(
        world_id=world_id,
        job_id=job_id,
        extraction_run_id=extraction_run_id,
        chapter_id=chapter_id,
        chapter_version_id=chapter_version_id,
        chapter_text=chapter_text,
        chapter_number=chapter_number
    )
