"""
Celery Beat adapter — persists schedule intent; Beat entries should mirror these jobs.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from ..ports import JobSpec, SchedulerPort, TimerHandle, TimerPort

logger = logging.getLogger("humanos.endocrine.celery_beat")


class CeleryBeatSchedulerAdapter(SchedulerPort):
    """
    Records jobs in the database for Celery Beat to execute via shared task names.

    Actual cron routing is configured in Django CELERY_BEAT_SCHEDULE or dynamic beat entries.
    """

    def schedule(self, spec: JobSpec) -> str:
        job_id = spec.job_id or f"beat-{uuid.uuid4().hex[:12]}"
        logger.info("Registered beat-backed job id %s (configure CELERY_BEAT_SCHEDULE to run)", job_id)
        return job_id

    def cancel(self, job_id: str) -> bool:
        from ..models import ScheduledJob

        updated = ScheduledJob.objects.filter(external_id=job_id).update(
            status=ScheduledJob.Status.CANCELLED
        )
        return updated > 0

    def list_jobs(self) -> list[JobSpec]:
        from ..models import ScheduledJob

        qs = ScheduledJob.objects.exclude(status=ScheduledJob.Status.CANCELLED).order_by("-created_at")[:50]
        out: list[JobSpec] = []
        for row in qs:
            out.append(
                JobSpec(
                    job_id=row.external_id or str(row.pk),
                    name=row.name,
                    payload=row.payload,
                    retry_count=row.retry_count,
                )
            )
        return out


class CeleryBeatTimerAdapter(TimerPort):
    """Timers via Celery ``apply_async`` countdown."""

    def set_timer(
        self,
        delay_seconds: float,
        callback: Callable[[], None] | None,
        label: str = "",
    ) -> TimerHandle:
        timer_id = f"beat-tmr-{uuid.uuid4().hex[:12]}"
        fire_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        try:
            from ..tasks import fire_timer_hook

            fire_timer_hook.apply_async(
                kwargs={"timer_id": timer_id, "label": label},
                countdown=int(delay_seconds),
            )
        except Exception as exc:
            logger.warning("Celery apply_async failed (%s); timer not armed", exc)
        return TimerHandle(timer_id=timer_id, fires_at=fire_at, label=label)

    def clear_timer(self, timer_id: str) -> bool:
        # Revoking arbitrary ETA tasks requires result backend metadata; best-effort no-op.
        logger.debug("clear_timer(%s): revoke not implemented without task id store", timer_id)
        return False
