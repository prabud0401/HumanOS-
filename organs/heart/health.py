"""
Heart Health Check — bus reachability and recent pulse.
"""

from datetime import timedelta

from django.utils import timezone

from core.pulse import HealthStatus

from .dna import get_heart_dna
from .models import HeartbeatRecord


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_heart_dna()
        details["stream_name"] = dna.stream_name
        details["heartbeat_interval_sec"] = dna.heartbeat_interval

        from .services import get_heart_service

        svc = get_heart_service()
        _ = svc.replay_recent(limit=1)
        details["replay_ok"] = True

        recent = timezone.now() - timedelta(seconds=dna.heartbeat_interval * 4)
        last = HeartbeatRecord.objects.filter(created_at__gte=recent).first()
        details["recent_heartbeat"] = last.beat_id if last else None

        if last is None and HeartbeatRecord.objects.exists():
            return (
                HealthStatus.DEGRADED,
                "No recent heartbeat record (bus may still be processing events)",
                details,
            )

        return HealthStatus.HEALTHY, "Heart operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Heart check failed: {exc}", details
