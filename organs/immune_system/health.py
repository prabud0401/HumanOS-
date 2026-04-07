"""
Immune System Health — Encryption readiness and open security incidents.
"""

from core.pulse import HealthStatus

from .dna import get_immune_system_dna
from .models import SecurityEvent
from .services import FernetEncryptionPort


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_immune_system_dna()
        enc = FernetEncryptionPort(algorithm=dna.encryption_algorithm)
        probe = enc.encrypt(b"ping", key_id="health")
        enc.decrypt(probe)
        details["encryption"] = "ok"

        open_incidents = SecurityEvent.objects.filter(
            status__in=[SecurityEvent.Status.OPEN, SecurityEvent.Status.INVESTIGATING]
        ).count()
        details["open_security_events"] = open_incidents

        if open_incidents > 10:
            return HealthStatus.DEGRADED, "Elevated count of open security events", details

        return HealthStatus.HEALTHY, "Immune system operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Immune system health check failed: {exc}", details
