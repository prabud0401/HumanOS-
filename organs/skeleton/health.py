"""
Skeleton Health — Template dir and project root reachable.
"""

from core.pulse import HealthStatus

from .dna import get_skeleton_dna


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_skeleton_dna()
        details["project_root"] = str(dna.project_root)
        details["template_dir"] = str(dna.template_dir)
        details["naming_conventions"] = list(dna.naming_conventions.keys())

        if not dna.project_root.exists():
            return HealthStatus.DEGRADED, "project_root does not exist on disk", details

        if not dna.template_dir.exists():
            return HealthStatus.DEGRADED, "template_dir does not exist — will create on demand", details

        return HealthStatus.HEALTHY, "Skeleton operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Skeleton health check failed: {exc}", details
