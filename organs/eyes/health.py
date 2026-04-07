"""
Eyes Health Check — dashboard service and widget registry.
"""

from core.pulse import HealthStatus

from .models import DashboardWidget


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        n = DashboardWidget.objects.filter(is_active=True).count()
        details["active_widgets"] = n
        from .dna import get_eyes_dna

        d = get_eyes_dna()
        details["theme"] = d.theme
        details["refresh_interval_sec"] = d.refresh_interval

        if n == 0:
            return (
                HealthStatus.DEGRADED,
                "No active dashboard widgets configured",
                details,
            )

        return HealthStatus.HEALTHY, "Eyes operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Eyes check failed: {exc}", details
