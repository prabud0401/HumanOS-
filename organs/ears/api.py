"""
Ears REST API — manual poll trigger and webhook intake (skeleton).
"""

import logging

logger = logging.getLogger("humanos.ears.api")

try:
    from ninja import Router

    router = Router(tags=["ears"])

    @router.get("/health")
    def ears_health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

    @router.post("/poll")
    def poll_now(request):
        from .services import get_ears_service

        n = get_ears_service().poll_calendars()
        return {"events_processed": n}

except ImportError:
    logger.debug("django-ninja not installed — ears API not registered")
    router = None
