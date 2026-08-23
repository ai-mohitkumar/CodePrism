import uuid
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
from models import (
    JobStatus, JobStatusResponse, UniversalResult
)
from languages.registry import LanguageRegistry

class JobQueueManager:
    _jobs: Dict[str, Dict] = {}
    _executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def submit_job(cls, language: str, code: str, stdin: str = "", filename: Optional[str] = None) -> str:
        job_id = f"cp_{uuid.uuid4().hex[:10]}"
        now = time.time()

        with cls._lock:
            cls._jobs[job_id] = {
                "job_id": job_id,
                "status": JobStatus.QUEUED,
                "progress": 5,
                "created_at": now,
                "updated_at": now,
                "result": None,
                "error": None
            }

        # Dispatch to worker pool
        cls._executor.submit(cls._process_job, job_id, language, code, stdin, filename)
        return job_id

    @classmethod
    def get_status(cls, job_id: str) -> Optional[JobStatusResponse]:
        with cls._lock:
            job_data = cls._jobs.get(job_id)
            if not job_data:
                return None
            return JobStatusResponse(
                job_id=job_data["job_id"],
                status=job_data["status"],
                progress=job_data["progress"],
                created_at=job_data["created_at"],
                updated_at=job_data["updated_at"],
                result=job_data["result"],
                error=job_data["error"]
            )

    @classmethod
    def _update_job(cls, job_id: str, status: JobStatus, progress: int, result: Optional[UniversalResult] = None, error: Optional[str] = None):
        with cls._lock:
            if job_id in cls._jobs:
                cls._jobs[job_id]["status"] = status
                cls._jobs[job_id]["progress"] = progress
                cls._jobs[job_id]["updated_at"] = time.time()
                if result is not None:
                    cls._jobs[job_id]["result"] = result
                if error is not None:
                    cls._jobs[job_id]["error"] = error

    @classmethod
    def _process_job(cls, job_id: str, language: str, code: str, stdin: str, filename: Optional[str]):
        try:
            cls._update_job(job_id, JobStatus.STARTING, 15)
            time.sleep(0.02)

            adapter = LanguageRegistry.get(language)
            if not adapter:
                cls._update_job(job_id, JobStatus.FAILED, 100, error=f"Unsupported language: {language}")
                return

            cls._update_job(job_id, JobStatus.COMPILING, 35)
            time.sleep(0.02)

            cls._update_job(job_id, JobStatus.RUNNING, 60)
            result = adapter.run_full_analysis(code, stdin=stdin, timeout_sec=6.0, filename=filename)

            cls._update_job(job_id, JobStatus.ANALYZING, 85)
            time.sleep(0.02)

            cls._update_job(job_id, JobStatus.COMPLETED, 100, result=result)

        except Exception as e:
            cls._update_job(job_id, JobStatus.FAILED, 100, error=str(e))
