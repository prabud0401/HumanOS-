"""
Hands Service — Orchestrates execution ports, agent delegation, and task persistence.
"""

from __future__ import annotations

import fnmatch
import logging
import uuid
from typing import Any

from django.db import transaction
from django.utils import timezone as dj_tz

from core.bus import emit

from .dna import get_hands_dna
from .models import AgentAction, Task, TaskExecution
from .ports import AgentDelegation, AgentPort, ExecutionContext, ExecutionPort, ExecutionResult

logger = logging.getLogger("humanos.hands.services")


class _NoopAgentPort(AgentPort):
    def delegate(self, delegation: AgentDelegation) -> str:
        return f"noop-{uuid.uuid4().hex[:8]}"

    def monitor(self, correlation_id: str):
        from .ports import AgentStatus

        return AgentStatus(healthy=True, active_jobs=0, details={"correlation_id": correlation_id})


class HandsService:
    """Enqueue, execute, and audit tasks using configured adapters."""

    def __init__(
        self,
        execution_by_kind: dict[str, ExecutionPort],
        agent: AgentPort | None = None,
    ):
        self._execution_by_kind = execution_by_kind
        self._agent = agent or _NoopAgentPort()

    def _select_adapter(self, action_type: str) -> ExecutionPort | None:
        if action_type.startswith("github.") or action_type.startswith("gh."):
            return self._execution_by_kind.get("github")
        if action_type.startswith("azure_devops.") or action_type.startswith("ado."):
            return self._execution_by_kind.get("azure_devops")
        return self._execution_by_kind.get("shell")

    def _action_allowed(self, action_type: str) -> bool:
        dna = get_hands_dna()
        for pattern in dna.allowed_actions:
            if fnmatch.fnmatch(action_type, pattern):
                return True
        return False

    def enqueue_from_decision(
        self,
        *,
        task_id: str,
        title: str,
        action_type: str,
        payload: dict[str, Any],
        source_event_id: str = "",
        decision_ref: str = "",
    ) -> Task:
        if not self._action_allowed(action_type):
            logger.warning("Action %s not in allowed_actions — queueing anyway as blocked", action_type)
        with transaction.atomic():
            task, _ = Task.objects.update_or_create(
                task_id=task_id,
                defaults={
                    "title": title,
                    "action_type": action_type,
                    "payload": payload,
                    "source_event_id": source_event_id,
                    "decision_ref": decision_ref,
                    "status": Task.Status.QUEUED,
                },
            )
        return task

    def run_task(self, task_id: str, *, dry_run: bool = False) -> TaskExecution:
        """Execute a single task and persist execution log."""
        task = Task.objects.get(task_id=task_id)
        adapter = self._select_adapter(task.action_type)
        if adapter is None:
            raise RuntimeError(f"No adapter for action_type={task.action_type}")

        ctx = ExecutionContext(
            task_id=task.task_id,
            action_type=task.action_type,
            payload=task.payload,
            dry_run=dry_run,
        )
        task.status = Task.Status.RUNNING
        task.started_at = dj_tz.now()
        task.save(update_fields=["status", "started_at", "updated_at"])

        ex_id = f"ex-{uuid.uuid4().hex[:12]}"
        result = adapter.execute(ctx)

        outcome = (
            TaskExecution.Outcome.SUCCESS
            if result.success
            else TaskExecution.Outcome.FAILURE
        )
        execution = TaskExecution.objects.create(
            task=task,
            execution_id=ex_id,
            adapter=result.metadata.get("adapter", type(adapter).__name__),
            outcome=outcome,
            stdout=result.stdout,
            stderr=result.stderr or result.message,
            exit_code=result.exit_code,
            metadata=result.metadata,
            duration_ms=result.metadata.get("duration_ms", 0.0),
        )

        if result.success:
            task.status = Task.Status.COMPLETED
            task.completed_at = dj_tz.now()
            task.save(update_fields=["status", "completed_at", "updated_at"])
            emit(
                "task.completed",
                "hands",
                payload={"task_id": task.task_id, "execution_id": ex_id},
            )
            emit(
                "action.executed",
                "hands",
                payload={"task_id": task.task_id, "action_type": task.action_type},
            )
        else:
            task.status = Task.Status.FAILED
            task.completed_at = dj_tz.now()
            task.save(update_fields=["status", "completed_at", "updated_at"])
            emit(
                "task.failed",
                "hands",
                payload={"task_id": task.task_id, "execution_id": ex_id, "message": result.message},
            )

        return execution

    def delegate_action(self, capability: str, payload: dict[str, Any]) -> AgentAction:
        corr = self._agent.delegate(AgentDelegation(capability=capability, payload=payload))
        action = AgentAction.objects.create(
            action_id=f"aa-{uuid.uuid4().hex[:12]}",
            agent_name="default",
            capability=capability,
            input_snapshot=payload,
            output_snapshot={},
            state=AgentAction.State.IN_PROGRESS,
            correlation_id=corr,
        )
        return action


_service: HandsService | None = None


def get_hands_service() -> HandsService:
    global _service
    if _service is not None:
        return _service

    from .adapters.azure_devops_adapter import AzureDevOpsAdapter
    from .adapters.github_adapter import GitHubAdapter
    from .adapters.shell_adapter import ShellAdapter

    _service = HandsService(
        execution_by_kind={
            "github": GitHubAdapter(),
            "azure_devops": AzureDevOpsAdapter(),
            "shell": ShellAdapter(),
        },
    )
    return _service
