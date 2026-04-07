"""
APScheduler adapter — in-process scheduling and timers.
"""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from ..ports import JobSpec, SchedulerPort, TimerHandle, TimerPort

logger = logging.getLogger("humanos.endocrine.apscheduler")

_scheduler: BackgroundScheduler | None = None
_lock = threading.Lock()


def _get_scheduler() -> BackgroundScheduler:
    global _scheduler
    with _lock:
        if _scheduler is None:
            _scheduler = BackgroundScheduler(timezone="UTC")
            _scheduler.start()
        return _scheduler


class APSchedulerAdapter(SchedulerPort, TimerPort):
    """Single adapter implementing both scheduler and timer ports."""

    def schedule(self, spec: JobSpec) -> str:
        sched = _get_scheduler()
        job_id = spec.job_id or f"job-{uuid.uuid4().hex[:12]}"
        if spec.cron:
            trigger = CronTrigger.from_crontab(spec.cron)
            sched.add_job(
                self._fire_placeholder,
                trigger=trigger,
                id=job_id,
                kwargs={"name": spec.name, "payload": spec.payload},
                replace_existing=True,
            )
        elif spec.run_at:
            run_at = spec.run_at
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=timezone.utc)
            sched.add_job(
                self._fire_placeholder,
                trigger=DateTrigger(run_date=run_at),
                id=job_id,
                kwargs={"name": spec.name, "payload": spec.payload},
                replace_existing=True,
            )
        else:
            raise ValueError("JobSpec requires cron or run_at")
        logger.info("Scheduled job %s (%s)", job_id, spec.name)
        return job_id

    def _fire_placeholder(self, name: str, payload: dict) -> None:
        from core.bus import emit

        emit("schedule.triggered", "endocrine", payload={"job_name": name, **payload})

    def cancel(self, job_id: str) -> bool:
        try:
            _get_scheduler().remove_job(job_id)
            return True
        except Exception:
            return False

    def list_jobs(self) -> list[JobSpec]:
        out: list[JobSpec] = []
        for j in _get_scheduler().get_jobs():
            out.append(JobSpec(job_id=j.id, name=str(j.name or j.id), payload={}))
        return out

    def set_timer(
        self,
        delay_seconds: float,
        callback: Callable[[], None] | None,
        label: str = "",
    ) -> TimerHandle:
        sched = _get_scheduler()
        timer_id = f"tmr-{uuid.uuid4().hex[:12]}"
        fire_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

        def _cb() -> None:
            from core.bus import emit

            if callback:
                try:
                    callback()
                except Exception:
                    logger.exception("Timer callback failed")
            emit("timer.expired", "endocrine", payload={"timer_id": timer_id, "label": label})

        sched.add_job(_cb, trigger=DateTrigger(run_date=fire_at), id=timer_id)
        return TimerHandle(timer_id=timer_id, fires_at=fire_at, label=label)

    def clear_timer(self, timer_id: str) -> bool:
        return self.cancel(timer_id)
