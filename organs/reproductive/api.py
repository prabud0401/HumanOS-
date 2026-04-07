"""
Reproductive REST API.
"""

import logging

logger = logging.getLogger("humanos.reproductive.api")

try:
    from ninja import Router

    router = Router(tags=["reproductive"])

    @router.post("/clone")
    def clone(request, body: dict):
        from .ports import CloneSpec
        from .services import get_reproductive_service

        spec = CloneSpec(
            name=body.get("name", "twin"),
            target_path=body.get("target_path", "."),
            branch=body.get("branch", "main"),
            options=body.get("options") or {},
        )
        clone_id = get_reproductive_service().create_clone(spec)
        return {"clone_id": clone_id}

    @router.post("/validate")
    def validate(request, body: dict):
        from .services import get_reproductive_service

        ok, errs = get_reproductive_service().validate(body.get("config") or {})
        return {"ok": ok, "errors": errs}

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — reproductive API not registered")
    router = None
