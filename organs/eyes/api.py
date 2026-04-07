"""
Eyes REST API — layout and widget JSON for the frontend.
"""

import logging

logger = logging.getLogger("humanos.eyes.api")

try:
    from ninja import Router

    router = Router(tags=["eyes"])

    @router.get("/health")
    def eyes_health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

    @router.get("/layout")
    def layout(request):
        from core.bus import emit

        from .services import get_eyes_service

        user = getattr(request, "user", None)
        uid = getattr(user, "id", None) if user is not None and getattr(user, "is_authenticated", False) else None

        emit("dashboard.viewed", "eyes", payload={"user_id": uid})
        return get_eyes_service().get_layout(user_id=uid)

    @router.get("/widget/{slug}")
    def widget(request, slug: str):
        from .services import get_eyes_service

        return get_eyes_service().render_widget(slug)

except ImportError:
    logger.debug("django-ninja not installed — eyes API not registered")
    router = None
