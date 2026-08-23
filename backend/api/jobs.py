import time
from fastapi import APIRouter, HTTPException
from models import (
    ExecuteRequest, JobSubmissionResponse, JobStatusResponse, JobStatus
)
from jobs.queue import JobQueueManager

router = APIRouter(prefix="/api/jobs", tags=["Job Queue & Cloud Scaling"])

@router.post("/submit", response_model=JobSubmissionResponse)
def submit_execution_job(req: ExecuteRequest):
    job_id = JobQueueManager.submit_job(
        language=req.language,
        code=req.code,
        stdin=req.stdin or "",
        filename=req.filename
    )
    return JobSubmissionResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        created_at=time.time(),
        message="Job successfully enqueued to worker pool."
    )

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    status_resp = JobQueueManager.get_status(job_id)
    if not status_resp:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return status_resp
