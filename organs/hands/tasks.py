"""
Hands Celery Tasks — Async task execution off the request/event path.
"""

import logging

logger = logging.getLogger("humanos.hands.tasks")

try:
    from celery import shared_task

    @shared_task(name="hands.execute_task")
    def execute_task(task_id: str, dry_run: bool = False) -> dict:
        from .services import get_hands_service

        service = get_hands_service()
        ex = service.run_task(task_id, dry_run=dry_run)
        return {"execution_id": ex.execution_id, "outcome": ex.outcome}

    @shared_task(name="hands.verify_task")
    def verify_task(task_id: str) -> dict:
        from .models import Task
        from .services import get_hands_service

        task = Task.objects.get(task_id=task_id)
        service = get_hands_service()
        adapter = service._select_adapter(task.action_type)
        if adapter is None:
            return {"success": False, "message": "no adapter"}
        from .ports import ExecutionContext

        ctx = ExecutionContext(task_id=task.task_id, action_type=task.action_type, payload=task.payload)
        r = adapter.verify(ctx)
        return {"success": r.success, "message": r.message, "metadata": r.metadata}

    @shared_task(name="hands.rollback_last")
    def rollback_last(task_id: str) -> dict:
        from .models import Task, TaskExecution
        from .services import get_hands_service

        task = Task.objects.get(task_id=task_id)
        last = TaskExecution.objects.filter(task=task).order_by("-created_at").first()
        if not last:
            return {"success": False, "message": "no execution"}
        service = get_hands_service()
        adapter = service._select_adapter(task.action_type)
        if adapter is None:
            return {"success": False, "message": "no adapter"}
        from .ports import ExecutionContext, ExecutionResult

        ctx = ExecutionContext(task_id=task.task_id, action_type=task.action_type, payload=task.payload)
        prior = ExecutionResult(
            success=last.outcome == TaskExecution.Outcome.SUCCESS,
            message="",
            stdout=last.stdout,
            stderr=last.stderr,
            exit_code=last.exit_code,
            metadata=last.metadata,
        )
        r = adapter.rollback(ctx, prior)
        return {"success": r.success, "message": r.message}

except ImportError:
    logger.debug("Celery not installed — hands tasks are stubs")

    def execute_task(task_id, dry_run=False):
        raise RuntimeError("Celery required for async hands tasks")

    def verify_task(task_id):
        raise RuntimeError("Celery required for async hands tasks")

    def rollback_last(task_id):
        raise RuntimeError("Celery required for async hands tasks")
