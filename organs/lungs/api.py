"""
Lungs REST API — ingestion triggers and job inspection.
"""

import logging

logger = logging.getLogger("humanos.lungs.api")

try:
    from ninja import Router

    router = Router(tags=["lungs"])

    @router.get("/health")
    def lungs_health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

    @router.post("/ingest")
    def ingest(request, body: dict):
        from .services import get_lungs_service

        job = get_lungs_service().ingest_meeting(
            job_id=body.get("job_id", ""),
            provider=body.get("provider", "teams"),
            meeting_id=body.get("meeting_id", ""),
            title=body.get("title", ""),
            metadata=body.get("metadata"),
        )
        return {"job_id": job.job_id, "status": job.status}

    @router.get("/jobs/{job_id}")
    def job_detail(request, job_id: str):
        from .models import IngestionJob

        j = IngestionJob.objects.get(job_id=job_id)
        return {
            "job_id": j.job_id,
            "source": j.source,
            "status": j.status,
            "retry_count": j.retry_count,
            "error_message": j.error_message,
            "artifact_count": j.artifacts.count(),
        }

except ImportError:
    logger.debug("django-ninja not installed — lungs API not registered")
    router = None
