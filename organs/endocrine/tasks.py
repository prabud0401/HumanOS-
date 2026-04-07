"""
Endocrine Celery tasks — deferred timer hooks and periodic checks.
"""

import logging

logger = logging.getLogger("humanos.endocrine.tasks")

try:
    from celery import shared_task

    @shared_task(name="endocrine.fire_timer_hook")
    def fire_timer_hook(timer_id: str, label: str = "") -> dict:
        from core.bus import emit

        emit("timer.expired", "endocrine", payload={"timer_id": timer_id, "label": label})
        return {"timer_id": timer_id}

    @shared_task(name="endocrine.check_due_reminders")
    def check_due_reminders() -> int:
        from django.utils import timezone as dj_tz

        from core.bus import emit

        from .models import Reminder

        now = dj_tz.now()
        n = 0
        for r in Reminder.objects.filter(delivered=False, fire_at__lte=now):
            emit(
                "reminder.due",
                "endocrine",
                payload={"reminder_id": r.pk, "title": r.title, "payload": r.payload},
            )
            r.delivered = True
            r.save(update_fields=["delivered"])
            n += 1
        return n

except ImportError:
    logger.debug("Celery not installed — endocrine tasks are stubs")

    def fire_timer_hook(timer_id, label=""):
        raise RuntimeError("Celery required for beat timer hooks")

    def check_due_reminders():
        raise RuntimeError("Celery required for reminder polling")
