"""
Local shell execution adapter — subprocess-based ExecutionPort.
"""

from __future__ import annotations

import logging
import shlex
import subprocess
import time
from pathlib import Path

from ..ports import ExecutionContext, ExecutionPort, ExecutionResult

logger = logging.getLogger("humanos.hands.adapters.shell")


class ShellAdapter(ExecutionPort):
    """Run whitelisted shell commands in a controlled working directory."""

    def __init__(self, cwd: str | Path | None = None, timeout_seconds: int = 120):
        self._cwd = Path(cwd) if cwd else Path.cwd()
        self._timeout = timeout_seconds

    def execute(self, ctx: ExecutionContext) -> ExecutionResult:
        cmd = ctx.payload.get("command")
        if not cmd or not isinstance(cmd, str):
            return ExecutionResult(
                success=False,
                message="payload.command required for shell adapter",
                metadata={"adapter": "shell"},
            )
        if ctx.dry_run:
            return ExecutionResult(
                success=True,
                message=f"Would run: {cmd}",
                metadata={"adapter": "shell", "cwd": str(self._cwd)},
            )
        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd if isinstance(cmd, str) else shlex.split(cmd),
                shell=isinstance(cmd, str),
                cwd=self._cwd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            elapsed = (time.monotonic() - start) * 1000
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                exit_code=proc.returncode,
                metadata={"adapter": "shell", "duration_ms": round(elapsed, 2)},
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                message=f"Command timed out after {self._timeout}s",
                metadata={"adapter": "shell"},
            )
        except Exception as exc:
            logger.exception("Shell execution failed")
            return ExecutionResult(
                success=False,
                message=str(exc),
                stderr=str(exc),
                metadata={"adapter": "shell"},
            )

    def rollback(self, ctx: ExecutionContext, last_result: ExecutionResult) -> ExecutionResult:
        undo = ctx.payload.get("rollback_command")
        if not undo:
            return ExecutionResult(
                success=True,
                message="No rollback_command provided — noop",
                metadata={"adapter": "shell"},
            )
        undo_ctx = ExecutionContext(
            task_id=ctx.task_id,
            action_type="shell.rollback",
            payload={"command": undo},
            dry_run=ctx.dry_run,
        )
        return self.execute(undo_ctx)

    def verify(self, ctx: ExecutionContext) -> ExecutionResult:
        path = ctx.payload.get("path")
        if not path:
            return ExecutionResult(success=True, message="No path to verify", metadata={"adapter": "shell"})
        exists = (self._cwd / str(path)).exists() if not Path(path).is_absolute() else Path(path).exists()
        return ExecutionResult(
            success=exists,
            message="exists" if exists else "missing",
            metadata={"adapter": "shell", "path": str(path)},
        )
