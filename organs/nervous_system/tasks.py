"""
Nervous System Celery Tasks — Heartbeat sweeps and bulk broadcast.
"""

import logging

logger = logging.getLogger("humanos.nervous.tasks")

try:
    from celery import shared_task

    @shared_task(name="nervous_system.sweep_stale_connections")
    def sweep_stale_connections() -> dict:
        from datetime import timedelta

        from django.utils import timezone as dj_tz

        from .dna import get_nervous_system_dna
        from .models import Connection
        from .services import get_nervous_system_service

        dna = get_nervous_system_dna()
        cutoff = dj_tz.now() - timedelta(seconds=dna.heartbeat_interval * 3)
        qs = Connection.objects.filter(state=Connection.State.OPEN, last_heartbeat__lt=cutoff)
        svc = get_nervous_system_service()
        closed = 0
        for c in qs:
            svc.close_connection(c.connection_id)
            closed += 1
        return {"closed": closed}

    @shared_task(name="nervous_system.broadcast")
    def broadcast(channel: str, event_type: str, payload: dict) -> dict:
        from core.bus import emit

        from .ports import Envelope
        from .services import get_nervous_system_service

        svc = get_nervous_system_service()
        env = Envelope(channel=channel, event_type=event_type, payload=payload)
        n = svc.publish_envelope(env)
        emit("signal.broadcast", "nervous_system", payload={"channel": channel, "event_type": event_type})
        return {"deliveries": n}

except ImportError:
    logger.debug("Celery not installed — nervous_system tasks are stubs")

    def sweep_stale_connections():
        raise RuntimeError("Celery required for nervous_system tasks")

    def broadcast(channel, event_type, payload):
        raise RuntimeError("Celery required for nervous_system tasks")
