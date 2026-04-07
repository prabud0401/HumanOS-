"""
Lungs Celery Tasks — async ingestion workloads.
"""

import logging

logger = logging.getLogger("humanos.lungs.tasks")

try:
    from celery import shared_task

    @shared_task(name="lungs.ingest_meeting")
    def ingest_meeting_task(
        job_id: str,
        provider: str,
        meeting_id: str,
        title: str = "",
        metadata: dict | None = None,
    ) -> dict:
        from .services import get_lungs_service

        job = get_lungs_service().ingest_meeting(
            job_id=job_id,
            provider=provider,
            meeting_id=meeting_id,
            title=title,
            metadata=metadata,
        )
        return {"job_id": job.job_id, "status": job.status}

    @shared_task(name="lungs.retry_job")
    def retry_job_task(job_id: str) -> dict:
        from .services import get_lungs_service

        job = get_lungs_service().retry_job(job_id)
        return {"job_id": job.job_id, "status": job.status, "retry_count": job.retry_count}

except ImportError:
    logger.debug("Celery not installed — lungs tasks are stubs")

    def ingest_meeting_task(job_id, provider, meeting_id, title="", metadata=None):
        raise RuntimeError("Celery required for lungs.ingest_meeting")

    def retry_job_task(job_id):
        raise RuntimeError("Celery required for lungs.retry_job")
