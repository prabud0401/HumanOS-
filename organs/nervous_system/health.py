"""
Nervous System Health — Open connections vs DNA limits.
"""

from core.pulse import HealthStatus

from .dna import get_nervous_system_dna
from .models import Connection


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_nervous_system_dna()
        open_n = Connection.objects.filter(state=Connection.State.OPEN).count()
        details["open_connections"] = open_n
        details["max_connections"] = dna.max_connections
        details["heartbeat_interval"] = dna.heartbeat_interval

        if open_n > dna.max_connections:
            return HealthStatus.UNHEALTHY, "Open connections exceed DNA max_connections", details

        ratio = open_n / dna.max_connections if dna.max_connections else 0
        if ratio > 0.95:
            return HealthStatus.DEGRADED, "Approaching max_connections", details

        return HealthStatus.HEALTHY, "Nervous system operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Nervous system health check failed: {exc}", details
