from datetime import datetime
from app.core.database import SessionLocal
from app.models.processing_job import ProcessingJob
from app.models.extraction_run import ExtractionRun
from app.core.constants import JobStatus, ExtractionRunStatus
from app.workers.celery_app import celery_app
from app.config.logging import get_logger

logger = get_logger(__name__)

def update_job_progress(job_id: str):
    """
    Rolls up status from all extraction runs attached to a job.
    As per ER diagram notes:
    rolls status to DONE only when every spawned extraction_run is DONE (any FAILED fails the job).
    """
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return

        runs = db.query(ExtractionRun).filter(ExtractionRun.processing_job_id == job_id).all()
        if not runs:
            return

        completed_count = sum(1 for r in runs if r.status == ExtractionRunStatus.DONE.value)
        failed_count = sum(1 for r in runs if r.status == ExtractionRunStatus.FAILED.value)

        job.chapters_completed = completed_count

        if failed_count > 0:
            job.status = JobStatus.FAILED.value
            job.completed_at = datetime.utcnow()
            first_fail = next(r for r in runs if r.status == ExtractionRunStatus.FAILED.value)
            job.error_message = first_fail.error_message
        elif completed_count >= len(runs) and len(runs) > 0:
            job.status = JobStatus.DONE.value
            job.completed_at = datetime.utcnow()

        db.commit()
    finally:
        db.close()


@celery_app.task(name="tasks.update_job_status")
def update_job_status_task(job_id: str):
    update_job_progress(job_id)
