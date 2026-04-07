"""
Eyes Celery Tasks — warm caches or precompute dashboard aggregates.
"""

import logging

logger = logging.getLogger("humanos.eyes.tasks")

try:
    from celery import shared_task

    @shared_task(name="eyes.warm_dashboard_cache")
    def warm_dashboard_cache(user_id: int | None = None) -> dict:
        from .services import get_eyes_service

        layout = get_eyes_service().get_layout(user_id=user_id)
        return {"widgets": len(layout.get("widgets", []))}

except ImportError:
    logger.debug("Celery not installed — eyes tasks are stubs")

    def warm_dashboard_cache(user_id=None):
        raise RuntimeError("Celery required for eyes.warm_dashboard_cache")
