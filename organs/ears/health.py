"""
Ears Health Check — listeners configured and poll path sane.
"""

from core.pulse import HealthStatus

from .dna import get_ears_dna
from .models import Listener


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_ears_dna()
        details["poll_interval_sec"] = dna.poll_interval
        details["watched_calendars_count"] = len(dna.watched_calendars)
        active = Listener.objects.filter(is_active=True).count()
        details["active_listeners"] = active

        if active == 0 and not dna.watched_calendars:
            return (
                HealthStatus.DEGRADED,
                "No active listeners and no watched_calendars in DNA",
                details,
            )

        return HealthStatus.HEALTHY, "Ears operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Ears check failed: {exc}", details
