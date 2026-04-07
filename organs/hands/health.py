"""
Hands Health — Execution adapters and queue depth.
"""

from core.pulse import HealthStatus

from .ports import ExecutionContext


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        from .dna import get_hands_dna
        from .models import Task
        from .services import get_hands_service

        dna = get_hands_dna()
        details["max_concurrent_tasks"] = dna.max_concurrent_tasks
        details["allowed_action_patterns"] = len(dna.allowed_actions)

        service = get_hands_service()
        ctx = ExecutionContext(task_id="health", action_type="health.verify", payload={})

        adapter_checks: dict[str, bool] = {}
        for name, adapter in service._execution_by_kind.items():
            if adapter:
                adapter_checks[name] = adapter.verify(ctx).success
        details["adapter_checks"] = adapter_checks

        running = Task.objects.filter(status=Task.Status.RUNNING).count()
        details["running_tasks"] = running
        if running > dna.max_concurrent_tasks:
            return (
                HealthStatus.DEGRADED,
                f"More running tasks ({running}) than DNA max_concurrent_tasks ({dna.max_concurrent_tasks})",
                details,
            )

        if adapter_checks and not all(adapter_checks.values()):
            return HealthStatus.DEGRADED, "One or more execution backends not fully configured", details

        return HealthStatus.HEALTHY, "Hands operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Hands health check failed: {exc}", details
