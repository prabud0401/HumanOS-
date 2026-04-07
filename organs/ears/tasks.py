"""
Ears Celery Tasks — scheduled polling for calendar and webhook-driven signals.
"""

import logging

logger = logging.getLogger("humanos.ears.tasks")

try:
    from celery import shared_task

    @shared_task(name="ears.poll_calendars")
    def poll_calendars() -> dict:
        from .services import get_ears_service

        n = get_ears_service().poll_calendars()
        return {"events_processed": n}

except ImportError:
    logger.debug("Celery not installed — ears tasks are stubs")

    def poll_calendars():
        raise RuntimeError("Celery required for ears.poll_calendars")
