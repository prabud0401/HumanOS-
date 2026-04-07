"""
Reproductive organ health.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        from .dna import get_reproductive_dna
        from .models import CloneInstance
        from .services import get_reproductive_service

        dna = get_reproductive_dna()
        details["template_repo"] = bool(dna.template_repo)
        details["clone_path"] = dna.clone_path
        details["clones"] = CloneInstance.objects.count()

        _ = get_reproductive_service()

        details["clone_backend"] = "git" if dna.template_repo else "docker"

        return HealthStatus.HEALTHY, "Reproductive organ operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Reproductive check failed: {exc}", details
