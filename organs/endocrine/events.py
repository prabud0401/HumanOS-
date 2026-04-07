"""
Endocrine events — time-based signals to the rest of HumanOS.
"""

import logging
from datetime import datetime

from core.bus import Event

logger = logging.getLogger("humanos.endocrine.events")

PUBLISHES = [
    "schedule.triggered",
    "reminder.due",
    "timer.expired",
]

SUBSCRIBES = [
    "schedule.create",
    "reminder.set",
]


def handle_event(event: Event) -> None:
    handlers = {
        "schedule.create": _on_schedule_create,
        "reminder.set": _on_reminder_set,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Endocrine received unhandled event: %s", event.type)


def _on_schedule_create(event: Event) -> None:
    from .ports import JobSpec
    from .services import get_endocrine_service

    p = event.payload or {}
    spec = JobSpec(
        job_id=p.get("job_id", ""),
        name=p.get("name", "unnamed"),
        cron=p.get("cron"),
        run_at=_parse_dt(p.get("run_at")),
        payload=p.get("payload") or {},
        retry_count=int(p.get("retry_count", 0)),
    )
    job_id = get_endocrine_service().schedule_job(spec)
    logger.info("Created schedule job %s", job_id)


def _on_reminder_set(event: Event) -> None:
    from .models import Reminder
    from .services import get_endocrine_service

    p = event.payload or {}
    title = p.get("title", "Reminder")
    fire_at = _parse_dt(p.get("fire_at"))
    if not fire_at:
        logger.error("reminder.set missing fire_at")
        return
    tz = p.get("timezone", "UTC")
    r = Reminder.objects.create(title=title, fire_at=fire_at, timezone=tz, payload=p.get("payload") or {})
    get_endocrine_service().arm_reminder(r)


def _parse_dt(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
