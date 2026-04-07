"""
Circulatory REST API — Django Ninja routes for pipelines and packets.
"""

import logging

logger = logging.getLogger("humanos.circulatory.api")

try:
    from ninja import Router

    router = Router(tags=["circulatory_system"])

    @router.get("/pipelines")
    def list_pipelines(request):
        from .models import Pipeline

        qs = Pipeline.objects.filter(is_active=True).values(
            "slug", "name", "source_organ", "target_organ"
        )
        return list(qs)

    @router.post("/deliver")
    def deliver(request, body: dict):
        from .ports import TransitEnvelope
        from .services import get_circulatory_service

        env = TransitEnvelope(
            packet_id=body.get("packet_id", ""),
            source_organ=body.get("source_organ", "api"),
            target_organ=body.get("target_organ", ""),
            payload=body.get("payload") or {},
            metadata=body.get("metadata") or {},
        )
        if not env.target_organ:
            return {"error": "target_organ required"}
        delivery_id = get_circulatory_service().deliver_envelope(env)
        return {"delivery_id": delivery_id}

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — circulatory API not registered")
    router = None
