"""
Hands Ports — Abstract interfaces for execution and agent delegation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionContext:
    """Context passed into execution adapters."""

    task_id: str
    action_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False


@dataclass
class ExecutionResult:
    """Normalized result from any execution backend."""

    success: bool
    message: str = ""
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ExecutionPort(ABC):
    """Port for executing and reversing automated work."""

    @abstractmethod
    def execute(self, ctx: ExecutionContext) -> ExecutionResult:
        """Run the action described by context."""

    @abstractmethod
    def rollback(self, ctx: ExecutionContext, last_result: ExecutionResult) -> ExecutionResult:
        """Best-effort undo of a prior execution."""

    @abstractmethod
    def verify(self, ctx: ExecutionContext) -> ExecutionResult:
        """Check post-conditions (e.g. PR merged, file exists)."""


@dataclass
class AgentDelegation:
    """Parameters for delegating work to another agent or worker."""

    capability: str
    payload: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300


@dataclass
class AgentStatus:
    """Observed state of a delegated agent run."""

    healthy: bool
    last_heartbeat: str | None = None
    active_jobs: int = 0
    details: dict[str, Any] = field(default_factory=dict)


class AgentPort(ABC):
    """Port for delegating work and monitoring remote agents."""

    @abstractmethod
    def delegate(self, delegation: AgentDelegation) -> str:
        """Start delegated work; returns correlation / job id."""

    @abstractmethod
    def monitor(self, correlation_id: str) -> AgentStatus:
        """Poll or stream status for a delegated job."""
