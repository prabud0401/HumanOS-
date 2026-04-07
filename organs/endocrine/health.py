"""
Endocrine health — scheduler backend and job backlog hints.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        from .dna import get_endocrine_dna
        from .models import ScheduledJob
        from .services import get_endocrine_service

        dna = get_endocrine_dna()
        details["timezone"] = dna.timezone
        from .services import _scheduler_backend

        details["scheduler_backend"] = _scheduler_backend()
        details["max_concurrent_jobs"] = dna.max_concurrent_jobs

        svc = get_endocrine_service()
        details["scheduler_adapter"] = type(svc._scheduler).__name__
        details["timer_adapter"] = type(svc._timers).__name__

        pending = ScheduledJob.objects.filter(status=ScheduledJob.Status.PENDING).count()
        details["pending_jobs"] = pending
        if pending > dna.max_concurrent_jobs * 10:
            return (
                HealthStatus.DEGRADED,
                "Large backlog of pending scheduled jobs",
                details,
            )

        return HealthStatus.HEALTHY, "Endocrine scheduler operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Endocrine check failed: {exc}", details
