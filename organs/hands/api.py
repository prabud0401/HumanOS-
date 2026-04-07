"""
Hands REST API — Django Ninja routes for task control and health.
"""

import logging

logger = logging.getLogger("humanos.hands.api")

try:
    from ninja import Router

    router = Router(tags=["hands"])

    @router.post("/tasks/enqueue")
    def enqueue_task(request, body: dict):
        from uuid import uuid4

        from .services import get_hands_service

        svc = get_hands_service()
        task_id = body.get("task_id") or f"task-{uuid4().hex[:12]}"
        task = svc.enqueue_from_decision(
            task_id=task_id,
            title=body.get("title", "API task"),
            action_type=body.get("action_type", "shell.run"),
            payload=body.get("payload", {}),
            source_event_id=body.get("source_event_id", ""),
            decision_ref=body.get("decision_ref", ""),
        )
        return {"task_id": task.task_id, "status": task.status}

    @router.post("/tasks/{task_id}/run")
    def run_task(request, task_id: str, body: dict | None = None):
        from .services import get_hands_service

        body = body or {}
        svc = get_hands_service()
        ex = svc.run_task(task_id, dry_run=bool(body.get("dry_run")))
        return {"execution_id": ex.execution_id, "outcome": ex.outcome}

    @router.get("/tasks/{task_id}")
    def get_task(request, task_id: str):
        from .models import Task

        t = Task.objects.get(task_id=task_id)
        return {
            "task_id": t.task_id,
            "title": t.title,
            "status": t.status,
            "action_type": t.action_type,
        }

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — hands API not registered")
    router = None
