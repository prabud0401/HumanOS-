"""
Immune System REST API — Django Ninja routes.
"""

import logging

logger = logging.getLogger("humanos.immune.api")

try:
    from ninja import Router

    router = Router(tags=["immune_system"])

    @router.post("/auth/login")
    def auth_login(request, body: dict):
        from .services import get_immune_system_service

        svc = get_immune_system_service()
        r = svc.login(body.get("principal", ""), body.get("credentials", {}))
        return {
            "authenticated": r.authenticated,
            "subject": r.subject,
            "roles": r.roles,
            "details": r.details,
        }

    @router.post("/authz/check")
    def authz_check(request, body: dict):
        from .services import get_immune_system_service

        svc = get_immune_system_service()
        ok = svc.can(
            body.get("subject", ""),
            body.get("action", "read"),
            body.get("resource", "*"),
            body.get("context"),
        )
        return {"allowed": ok}

    @router.post("/crypto/encrypt")
    def crypto_encrypt(request, body: dict):
        import base64

        from .services import get_immune_system_service

        data = (body.get("data") or "").encode()
        blob = get_immune_system_service().seal(data)
        return {
            "key_id": blob.key_id,
            "ciphertext_b64": base64.b64encode(blob.ciphertext).decode("ascii"),
        }

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — immune_system API not registered")
    router = None
