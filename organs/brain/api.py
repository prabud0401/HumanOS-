"""
Brain REST API — Django Ninja endpoints for the Brain organ.
"""

import logging

logger = logging.getLogger("humanos.brain.api")

try:
    from ninja import Router

    router = Router(tags=["brain"])

    @router.post("/analyze")
    def analyze(request, body: dict):
        """Analyze context and return structured insights."""
        from .services import get_brain_service
        service = get_brain_service()
        result = service.analyze(body.get("context", ""))
        return result

    @router.post("/decide")
    def decide(request, body: dict):
        """Make a decision based on analysis."""
        from .services import get_brain_service
        service = get_brain_service()
        return service.decide(body.get("analysis", {}), body.get("constraints"))

    @router.post("/summarize")
    def summarize(request, body: dict):
        """Summarize a text."""
        from .services import get_brain_service
        service = get_brain_service()
        return {"summary": service.summarize(body.get("text", ""))}

    @router.get("/health")
    def health(request):
        """Brain health check endpoint."""
        from .health import check
        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — brain API not registered")
    router = None
