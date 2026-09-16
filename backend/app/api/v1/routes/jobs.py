from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_job
from app.models.processing_job import ProcessingJob
from app.schemas.job import JobResponse, JobStatusResponse
from app.services.job_service import JobService

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job: ProcessingJob = Depends(get_current_user_job)):
    return job

@router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(
    job: ProcessingJob = Depends(get_current_user_job),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    status_info = service.get_job_status(job.id)
    return JobStatusResponse(**status_info)
