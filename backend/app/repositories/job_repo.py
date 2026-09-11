from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.processing_job import ProcessingJob
from app.core.constants import JobStatus
from app.repositories.base import BaseRepository

class JobRepository(BaseRepository[ProcessingJob]):
    def __init__(self, db: Session):
        super().__init__(ProcessingJob, db)

    def get_by_world(self, world_id: str) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.world_id == world_id
        ).order_by(ProcessingJob.created_at.desc()).all()

    def mark_started(self, job_id: str) -> Optional[ProcessingJob]:
        job = self.get(job_id)
        if job:
            job.status = JobStatus.PROCESSING.value
            job.started_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(job)
        return job

    def update_progress(self, job_id: str, completed: int, total: Optional[int] = None) -> Optional[ProcessingJob]:
        job = self.get(job_id)
        if job:
            job.chapters_completed = completed
            if total is not None:
                job.chapters_total = total
            self.db.commit()
            self.db.refresh(job)
        return job

    def mark_completed(self, job_id: str) -> Optional[ProcessingJob]:
        job = self.get(job_id)
        if job:
            job.status = JobStatus.DONE.value
            job.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(job)
        return job

    def mark_failed(self, job_id: str, error_message: str) -> Optional[ProcessingJob]:
        job = self.get(job_id)
        if job:
            job.status = JobStatus.FAILED.value
            job.completed_at = datetime.utcnow()
            job.error_message = error_message
            self.db.commit()
            self.db.refresh(job)
        return job
