"""
Endocrine service — wires scheduler and timer ports to domain models.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from core.bus import emit
from core.dna_loader import get_dna

from .dna import get_endocrine_dna
from .models import Reminder, Schedule, ScheduledJob
from .ports import JobSpec, SchedulerPort, TimerHandle, TimerPort

logger = logging.getLogger("humanos.endocrine.services")


def _scheduler_backend() -> str:
    raw = getattr(get_dna(), "_raw", {}) or {}
    endo = raw.get("endocrine")
    if not isinstance(endo, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            endo = organs.get("endocrine", {})
        if not isinstance(endo, dict):
            endo = {}
    return str(endo.get("scheduler_backend", "apscheduler"))


class EndocrineService:
    """Orchestrates scheduling adapters."""

    def __init__(self, scheduler: SchedulerPort, timers: TimerPort):
        self._scheduler = scheduler
        self._timers = timers

    def schedule_job(self, spec: JobSpec) -> str:
        dna = get_endocrine_dna()
        if spec.retry_count == 0 and dna.default_retry_count:
            spec = JobSpec(
                job_id=spec.job_id,
                name=spec.name,
                cron=spec.cron,
                run_at=spec.run_at,
                payload=spec.payload,
                retry_count=dna.default_retry_count,
            )
        job_id = self._scheduler.schedule(spec)
        sched = None
        if spec.cron:
            slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in job_id)[:128]
            sched, _ = Schedule.objects.get_or_create(
                slug=slug or "schedule",
                defaults={
                    "name": spec.name,
                    "cron_expression": spec.cron or "* * * * *",
                    "timezone": get_endocrine_dna().timezone,
                },
            )
        ScheduledJob.objects.create(
            external_id=job_id,
            schedule=sched,
            name=spec.name,
            status=ScheduledJob.Status.PENDING,
            payload=spec.payload,
            next_run_at=spec.run_at,
            retry_count=spec.retry_count,
        )
        return job_id

    def arm_reminder(self, reminder: Reminder) -> TimerHandle:
        """Schedule bus emit when reminder fires."""
        now = datetime.now(timezone.utc)
        fire_at = reminder.fire_at
        if fire_at.tzinfo is None:
            fire_at = fire_at.replace(tzinfo=timezone.utc)
        delay = max(0.0, (fire_at - now).total_seconds())

        def _fire() -> None:
            emit(
                "reminder.due",
                "endocrine",
                payload={
                    "reminder_id": reminder.pk,
                    "title": reminder.title,
                    "payload": reminder.payload,
                },
            )

        return self._timers.set_timer(delay, _fire, label=reminder.title[:200])

    def cancel_job(self, job_id: str) -> bool:
        return self._scheduler.cancel(job_id)

    def list_jobs(self) -> list[JobSpec]:
        return self._scheduler.list_jobs()


_service: EndocrineService | None = None


def get_endocrine_service() -> EndocrineService:
    global _service
    if _service is not None:
        return _service

    dna = get_endocrine_dna()
    if _scheduler_backend() == "celery_beat":
        from .adapters.celery_beat_adapter import CeleryBeatSchedulerAdapter, CeleryBeatTimerAdapter

        sched = CeleryBeatSchedulerAdapter()
        tmr = CeleryBeatTimerAdapter()
    else:
        from .adapters.apscheduler_adapter import APSchedulerAdapter

        combo = APSchedulerAdapter()
        sched = combo
        tmr = combo

    _service = EndocrineService(scheduler=sched, timers=tmr)
    return _service
