"""
Digestive System REST API — Django Ninja routes.
"""

import logging

logger = logging.getLogger("humanos.digestive.api")

try:
    from ninja import Router

    router = Router(tags=["digestive_system"])

    @router.post("/process")
    def process(request, body: dict):
        from .services import get_digestive_system_service

        job = get_digestive_system_service().run_job(
            body.get("uri", ""),
            body.get("format", "vtt"),
        )
        return {"job_id": job.job_id, "status": job.status, "error": job.error_message}

    @router.get("/jobs/{job_id}")
    def get_job(request, job_id: str):
        from .models import ProcessingJob

        j = ProcessingJob.objects.get(job_id=job_id)
        return {
            "job_id": j.job_id,
            "status": j.status,
            "format": j.format,
            "stats": j.stats,
            "error": j.error_message,
        }

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — digestive_system API not registered")
    router = None
