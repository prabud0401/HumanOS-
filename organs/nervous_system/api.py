"""
Nervous System REST API — Django Ninja routes.
"""

import logging

logger = logging.getLogger("humanos.nervous.api")

try:
    from ninja import Router

    router = Router(tags=["nervous_system"])

    @router.post("/connections/open")
    def open_connection(request, body: dict):
        from .models import Connection
        from .services import get_nervous_system_service

        svc = get_nervous_system_service()
        c = svc.open_connection(
            transport=body.get("transport", Connection.Transport.SSE),
            channels=body.get("channels", ["*"]),
            remote_addr=body.get("remote_addr"),
            user_agent=body.get("user_agent", ""),
        )
        return {"connection_id": c.connection_id, "transport": c.transport}

    @router.post("/connections/{connection_id}/close")
    def close_connection(request, connection_id: str):
        from .services import get_nervous_system_service

        get_nervous_system_service().close_connection(connection_id)
        return {"ok": True}

    @router.post("/broadcast")
    def broadcast(request, body: dict):
        from .ports import Envelope
        from .services import get_nervous_system_service

        env = Envelope(
            channel=body.get("channel", "default"),
            event_type=body.get("event_type", "message"),
            payload=body.get("payload", {}),
        )
        n = get_nervous_system_service().publish_envelope(env)
        return {"deliveries": n}

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — nervous_system API not registered")
    router = None
