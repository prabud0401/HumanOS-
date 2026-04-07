"""
Azure DevOps REST adapter — pipelines, repos, and work items.
"""

from __future__ import annotations

import logging
import os

from ..ports import ExecutionContext, ExecutionPort, ExecutionResult

logger = logging.getLogger("humanos.hands.adapters.azure_devops")


class AzureDevOpsAdapter(ExecutionPort):
    """Execute Azure DevOps operations using PAT + organization URL."""

    def __init__(
        self,
        organization_url: str | None = None,
        pat: str | None = None,
        project: str | None = None,
    ):
        self._org = (organization_url or os.environ.get("AZURE_DEVOPS_ORG_URL", "")).rstrip("/")
        self._pat = pat or os.environ.get("AZURE_DEVOPS_PAT", "")
        self._project = project or os.environ.get("AZURE_DEVOPS_PROJECT", "")

    def execute(self, ctx: ExecutionContext) -> ExecutionResult:
        if not self._pat or not self._org:
            return ExecutionResult(
                success=False,
                message="Azure DevOps PAT or ORG_URL not configured",
                metadata={"adapter": "azure_devops"},
            )
        if ctx.dry_run:
            return ExecutionResult(
                success=True,
                message="Dry run — no Azure DevOps API call",
                metadata={"adapter": "azure_devops"},
            )
        logger.info("Azure DevOps execute %s task=%s", ctx.action_type, ctx.task_id)
        return ExecutionResult(
            success=True,
            message=f"Azure DevOps action {ctx.action_type} accepted (stub)",
            metadata={
                "adapter": "azure_devops",
                "project": self._project,
            },
        )

    def rollback(self, ctx: ExecutionContext, last_result: ExecutionResult) -> ExecutionResult:
        return ExecutionResult(
            success=False,
            message="Azure DevOps rollback not implemented for this action",
            stderr=str(last_result.metadata),
            metadata={"adapter": "azure_devops"},
        )

    def verify(self, ctx: ExecutionContext) -> ExecutionResult:
        ok = bool(self._pat and self._org)
        return ExecutionResult(
            success=ok,
            message="Configured" if ok else "Missing credentials",
            metadata={"adapter": "azure_devops"},
        )
