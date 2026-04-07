"""
Endocrine ports — Scheduling and timer abstractions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable


@dataclass
class JobSpec:
    """Definition of work to run on a schedule or once."""

    job_id: str
    name: str
    cron: str | None = None
    run_at: datetime | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0


@dataclass
class TimerHandle:
    """Reference to a one-shot or recurring timer."""

    timer_id: str
    fires_at: datetime
    label: str = ""


class SchedulerPort(ABC):
    """Port for cron-like and one-shot job scheduling."""

    @abstractmethod
    def schedule(self, spec: JobSpec) -> str:
        """Register a job; returns scheduler-assigned id."""

    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled job; returns True if removed."""

    @abstractmethod
    def list_jobs(self) -> list[JobSpec]:
        """List active scheduled jobs (best-effort snapshot)."""


class TimerPort(ABC):
    """Port for relative timers (wake-ups, debounced triggers)."""

    @abstractmethod
    def set_timer(
        self,
        delay_seconds: float,
        callback: Callable[[], None] | None,
        label: str = "",
    ) -> TimerHandle:
        """Fire after delay; callback invoked in adapter context (may be async)."""

    @abstractmethod
    def clear_timer(self, timer_id: str) -> bool:
        """Cancel a pending timer."""
