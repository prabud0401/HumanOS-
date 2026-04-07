"""
Skeleton Celery Tasks — Async scaffolding and validation.
"""

import logging

logger = logging.getLogger("humanos.skeleton.tasks")

try:
    from celery import shared_task

    @shared_task(name="skeleton.scaffold")
    def scaffold(slug: str, template_key: str | None, variables: dict | None = None) -> dict:
        from .services import get_skeleton_service

        svc = get_skeleton_service()
        res = svc.scaffold_project(slug, template_key, variables or {})
        return {"success": res.success, "message": res.message, "paths": res.created_paths}

    @shared_task(name="skeleton.validate_structure")
    def validate_structure(root_path: str, layout: dict) -> dict:
        from pathlib import Path

        from .services import LocalProjectPort

        port = LocalProjectPort()
        report = port.validate_structure(Path(root_path), layout)
        return {
            "valid": report.valid,
            "missing": report.missing,
            "unexpected": report.unexpected,
        }

except ImportError:
    logger.debug("Celery not installed — skeleton tasks are stubs")

    def scaffold(slug, template_key, variables=None):
        raise RuntimeError("Celery required for async skeleton tasks")

    def validate_structure(root_path, layout):
        raise RuntimeError("Celery required for async skeleton tasks")
