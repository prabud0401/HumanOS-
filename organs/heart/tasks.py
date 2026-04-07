"""
Heart Celery Tasks — heartbeat pulse and stream maintenance.
"""

import logging

logger = logging.getLogger("humanos.heart.tasks")

try:
    from celery import shared_task

    @shared_task(name="heart.emit_heartbeat")
    def emit_heartbeat() -> dict:
        """Record a heartbeat row and emit heartbeat.pulse on the bus."""
        from core.bus import get_bus

        from .services import get_heart_service

        bus = get_bus()
        wildcard = 0
        handlers = getattr(bus, "_handlers", None)
        if isinstance(handlers, dict):
            wildcard = len(handlers.get("*", []))

        svc = get_heart_service()
        rec = svc.record_pulse(wildcard_handlers=wildcard)
        return {"beat_id": rec.beat_id, "status": rec.status}

    @shared_task(name="heart.trim_old_event_logs")
    def trim_old_event_logs() -> dict:
        """Delete EventLog rows older than DNA max_event_age (best-effort)."""
        from datetime import timedelta

        from django.utils import timezone

        from .dna import get_heart_dna
        from .models import EventLog

        dna = get_heart_dna()
        cutoff = timezone.now() - timedelta(seconds=dna.max_event_age)
        deleted, _ = EventLog.objects.filter(received_at__lt=cutoff).delete()
        return {"deleted": deleted, "cutoff": cutoff.isoformat()}

except ImportError:
    logger.debug("Celery not installed — heart tasks are stubs")

    def emit_heartbeat():
        raise RuntimeError("Celery required for heart.emit_heartbeat")

    def trim_old_event_logs():
        raise RuntimeError("Celery required for heart.trim_old_event_logs")
