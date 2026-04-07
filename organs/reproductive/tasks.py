"""
Reproductive Celery tasks — long-running clone and export jobs.
"""

import logging

logger = logging.getLogger("humanos.reproductive.tasks")

try:
    from celery import shared_task

    @shared_task(name="reproductive.async_clone")
    def async_clone(name: str, target_path: str, branch: str = "main") -> dict:
        from .ports import CloneSpec
        from .services import get_reproductive_service

        spec = CloneSpec(name=name, target_path=target_path, branch=branch)
        clone_id = get_reproductive_service().create_clone(spec)
        return {"clone_id": clone_id}

    @shared_task(name="reproductive.export_template_task")
    def export_template_task(output_path: str) -> str:
        from .services import get_reproductive_service

        # Export via underlying clone port
        port = get_reproductive_service()._clone
        return port.export_template(output_path)

except ImportError:
    logger.debug("Celery not installed — reproductive tasks are stubs")

    def async_clone(name, target_path, branch="main"):
        raise RuntimeError("Celery required for reproductive async clone")

    def export_template_task(output_path):
        raise RuntimeError("Celery required for reproductive export")
