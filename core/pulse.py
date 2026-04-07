"""
Pulse Monitor — Health check system for all organs.

Every organ registers a health check function. The Pulse Monitor
runs them periodically and reports overall system health. If an organ
is unhealthy, the system degrades gracefully.
"""

import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
from datetime import datetime, timezone

logger = logging.getLogger("humanos.pulse")


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class OrganHealth:
    organ: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    last_checked: str = ""
    response_time_ms: float = 0.0
    details: dict = field(default_factory=dict)


@dataclass
class SystemHealth:
    status: HealthStatus
    organs: dict[str, OrganHealth]
    checked_at: str
    healthy_count: int = 0
    degraded_count: int = 0
    unhealthy_count: int = 0


HealthCheckFn = Callable[[], tuple[HealthStatus, str, dict]]


class PulseMonitor:
    """Central health monitor — checks all registered organs."""

    def __init__(self):
        self._checks: dict[str, HealthCheckFn] = {}

    def register(self, organ_name: str, check_fn: HealthCheckFn) -> None:
        """Register an organ's health check function."""
        self._checks[organ_name] = check_fn
        logger.debug("Registered health check for '%s'", organ_name)

    def unregister(self, organ_name: str) -> None:
        self._checks.pop(organ_name, None)

    def check_organ(self, organ_name: str) -> OrganHealth:
        """Check a single organ's health."""
        fn = self._checks.get(organ_name)
        if fn is None:
            return OrganHealth(organ=organ_name, status=HealthStatus.UNKNOWN, message="No health check registered")

        start = time.monotonic()
        try:
            status, message, details = fn()
            elapsed = (time.monotonic() - start) * 1000
            return OrganHealth(
                organ=organ_name,
                status=status,
                message=message,
                last_checked=datetime.now(timezone.utc).isoformat(),
                response_time_ms=round(elapsed, 2),
                details=details,
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.exception("Health check failed for '%s'", organ_name)
            return OrganHealth(
                organ=organ_name,
                status=HealthStatus.UNHEALTHY,
                message=str(exc),
                last_checked=datetime.now(timezone.utc).isoformat(),
                response_time_ms=round(elapsed, 2),
            )

    def check_all(self) -> SystemHealth:
        """Check all organs and return system-wide health."""
        organs = {}
        for name in self._checks:
            organs[name] = self.check_organ(name)

        healthy = sum(1 for o in organs.values() if o.status == HealthStatus.HEALTHY)
        degraded = sum(1 for o in organs.values() if o.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for o in organs.values() if o.status == HealthStatus.UNHEALTHY)

        if unhealthy > 0:
            overall = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return SystemHealth(
            status=overall,
            organs=organs,
            checked_at=datetime.now(timezone.utc).isoformat(),
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy,
        )

    @property
    def registered_organs(self) -> list[str]:
        return list(self._checks.keys())


# Global instance
_monitor = PulseMonitor()


def get_pulse() -> PulseMonitor:
    return _monitor


def register_organ_health(organ_name: str, check_fn: HealthCheckFn) -> None:
    _monitor.register(organ_name, check_fn)
