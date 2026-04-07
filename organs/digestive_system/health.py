"""
Digestive System Health — Parser backends and recent failure rate.
"""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone as dj_tz

from core.pulse import HealthStatus

from .dna import get_digestive_system_dna
from .models import ProcessingJob


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_digestive_system_dna()
        details["supported_formats"] = dna.supported_formats
        details["max_file_size"] = dna.max_file_size
        details["nlp_model"] = dna.nlp_model

        recent = dj_tz.now() - timedelta(hours=24)
        window = ProcessingJob.objects.filter(created_at__gte=recent)
        stats = window.aggregate(
            failed=Count("id", filter=Q(status=ProcessingJob.Status.FAILED)),
            total=Count("id"),
        )
        details["failed_24h"] = stats["failed"] or 0
        details["total_24h"] = stats["total"] or 0

        total = details["total_24h"]
        failed = details["failed_24h"]
        if total > 5 and failed / total > 0.5:
            return HealthStatus.DEGRADED, "High processing failure rate in last 24h", details

        return HealthStatus.HEALTHY, "Digestive system operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Digestive system health check failed: {exc}", details
