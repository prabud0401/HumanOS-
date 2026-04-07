"""
GitHub REST API adapter — implements ExecutionPort for repository automation.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..ports import ExecutionContext, ExecutionPort, ExecutionResult

logger = logging.getLogger("humanos.hands.adapters.github")


class GitHubAdapter(ExecutionPort):
    """Execute GitHub operations via the REST API (token from environment)."""

    def __init__(self, token: str | None = None, api_base: str = "https://api.github.com"):
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._api_base = api_base.rstrip("/")

    def execute(self, ctx: ExecutionContext) -> ExecutionResult:
        if not self._token:
            return ExecutionResult(
                success=False,
                message="GITHUB_TOKEN not set",
                metadata={"adapter": "github"},
            )
        if ctx.dry_run:
            return ExecutionResult(
                success=True,
                message="Dry run — no GitHub API call",
                metadata={"adapter": "github", "would_run": ctx.action_type},
            )
        # Production: map action_type to httpx calls (issues, PRs, workflows)
        logger.info("GitHub execute %s for task %s", ctx.action_type, ctx.task_id)
        return ExecutionResult(
            success=True,
            message=f"GitHub action {ctx.action_type} accepted (stub)",
            metadata={"adapter": "github", "payload_keys": list(ctx.payload.keys())},
        )

    def rollback(self, ctx: ExecutionContext, last_result: ExecutionResult) -> ExecutionResult:
        logger.warning("GitHub rollback requested for task %s", ctx.task_id)
        return ExecutionResult(
            success=True,
            message="Rollback acknowledged (implement per action_type)",
            metadata={"adapter": "github", "prior": last_result.metadata},
        )

    def verify(self, ctx: ExecutionContext) -> ExecutionResult:
        return ExecutionResult(
            success=bool(self._token),
            message="Token present" if self._token else "Not configured",
            metadata={"adapter": "github"},
        )
