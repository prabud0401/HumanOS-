"""
Endocrine REST API — schedules and reminders.
"""

import logging

logger = logging.getLogger("humanos.endocrine.api")

try:
    from ninja import Router

    router = Router(tags=["endocrine"])

    @router.post("/schedule")
    def create_schedule(request, body: dict):
        from datetime import datetime

        from .ports import JobSpec
        from .services import get_endocrine_service

        run_at = body.get("run_at")
        parsed = datetime.fromisoformat(run_at.replace("Z", "+00:00")) if run_at else None
        spec = JobSpec(
            job_id=body.get("job_id", ""),
            name=body.get("name", "api-job"),
            cron=body.get("cron"),
            run_at=parsed,
            payload=body.get("payload") or {},
        )
        job_id = get_endocrine_service().schedule_job(spec)
        return {"job_id": job_id}

    @router.get("/jobs")
    def list_jobs(request):
        from .services import get_endocrine_service

        jobs = get_endocrine_service().list_jobs()
        return [{"job_id": j.job_id, "name": j.name} for j in jobs]

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — endocrine API not registered")
    router = None
