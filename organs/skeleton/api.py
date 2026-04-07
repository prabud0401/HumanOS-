"""
Skeleton REST API — Django Ninja routes.
"""

import logging

logger = logging.getLogger("humanos.skeleton.api")

try:
    from ninja import Router

    router = Router(tags=["skeleton"])

    @router.get("/templates")
    def list_templates(request):
        from .services import LocalTemplatePort

        port = LocalTemplatePort()
        return [{"key": t.key, "label": t.label, "version": t.version} for t in port.list_templates()]

    @router.post("/scaffold")
    def scaffold(request, body: dict):
        from .services import get_skeleton_service

        svc = get_skeleton_service()
        res = svc.scaffold_project(
            body.get("slug", "new-project"),
            body.get("template_key"),
            body.get("variables", {}),
        )
        return {"success": res.success, "message": res.message, "paths": res.created_paths}

    @router.post("/config")
    def set_config(request, body: dict):
        from .models import Project
        from .services import get_skeleton_service

        svc = get_skeleton_service()
        proj = None
        if body.get("project_slug"):
            proj = Project.objects.get(slug=body["project_slug"])
        entry = svc.set_config(body["key"], body.get("value"), project=proj)
        return {"key": entry.key, "scope": entry.scope}

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — skeleton API not registered")
    router = None
