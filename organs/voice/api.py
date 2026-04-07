"""
Voice REST API — manual notification tests and channel introspection.
"""

import logging

logger = logging.getLogger("humanos.voice.api")

try:
    from ninja import Router

    router = Router(tags=["voice"])

    @router.get("/health")
    def voice_health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

    @router.post("/send")
    def send_now(request, body: dict):
        from .ports import OutboundMessage
        from .services import get_voice_service

        msg = OutboundMessage(
            subject=body.get("subject", ""),
            body=body.get("body", ""),
            recipient=body.get("recipient", ""),
            metadata=body.get("metadata") or {},
        )
        r = get_voice_service().send(body.get("channel", "default"), msg)
        return {"ok": r.ok, "error": r.error, "provider_message_id": r.provider_message_id}

except ImportError:
    logger.debug("django-ninja not installed — voice API not registered")
    router = None
