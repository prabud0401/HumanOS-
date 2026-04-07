"""
Heart REST API — Django Ninja routes for bus audit and replay.
"""

import logging

logger = logging.getLogger("humanos.heart.api")

try:
    from ninja import Router

    router = Router(tags=["heart"])

    @router.get("/health")
    def heart_health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

    @router.get("/replay")
    def replay(request, limit: int = 100, after_id: str | None = None):
        from .services import get_heart_service

        events = get_heart_service().replay_recent(start_after_id=after_id, limit=limit)
        return {
            "count": len(events),
            "events": [e.to_dict() for e in events],
        }

    @router.get("/dna")
    def heart_dna(request):
        from .dna import get_heart_dna

        d = get_heart_dna()
        return {
            "heartbeat_interval": d.heartbeat_interval,
            "max_event_age": d.max_event_age,
            "stream_name": d.stream_name,
            "redis_url_configured": bool(d.redis_url),
        }

except ImportError:
    logger.debug("django-ninja not installed — heart API not registered")
    router = None
