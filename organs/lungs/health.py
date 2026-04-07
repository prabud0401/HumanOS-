"""
Lungs Health Check — download path writable and recent job stats.
"""

from pathlib import Path

from core.pulse import HealthStatus

from .dna import get_lungs_dna
from .models import IngestionJob


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_lungs_dna()
        path: Path = dna.download_path
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".lungs_health_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        details["download_path"] = str(path.resolve())
        details["max_concurrent_downloads"] = dna.max_concurrent_downloads

        failed_recent = IngestionJob.objects.filter(status=IngestionJob.Status.FAILED).count()
        details["failed_jobs_total"] = failed_recent

        if failed_recent > 50:
            return (
                HealthStatus.DEGRADED,
                "Many failed ingestion jobs — review logs",
                details,
            )

        return HealthStatus.HEALTHY, "Lungs operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Lungs check failed: {exc}", details
