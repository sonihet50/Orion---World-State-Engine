from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.processing_job import ProcessingJob
from app.repositories.job_repo import JobRepository

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)

    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        return self.job_repo.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[dict]:
        job = self.job_repo.get(job_id)
        if not job:
            return None
        return {
            "id": job.id,
            "status": job.status,
            "progress_current": job.chapters_completed,
            "progress_total": job.chapters_total,
            "error_message": job.error_message
        }

    def list_jobs(self, world_id: str) -> List[ProcessingJob]:
        return self.job_repo.get_by_world(world_id)
