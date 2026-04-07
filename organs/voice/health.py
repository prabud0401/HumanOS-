"""
Voice Health Check — channel configs structurally valid (no outbound send).
"""

from core.pulse import HealthStatus

from .dna import get_voice_dna
from .models import Channel


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        dna = get_voice_dna()
        details["default_channel"] = dna.default_channel
        details["cooldown_sec"] = dna.notification_cooldown

        channels = list(Channel.objects.filter(is_active=True))
        if not channels:
            return (
                HealthStatus.DEGRADED,
                "No active notification channels configured",
                details,
            )

        from .adapters import email_adapter, slack_adapter, teams_chat_adapter

        bad: list[str] = []
        for ch in channels:
            cfg = ch.config or {}
            if ch.kind == Channel.Kind.SLACK:
                ok = slack_adapter.validate_config(cfg)
            elif ch.kind == Channel.Kind.EMAIL:
                ok = email_adapter.validate_config(cfg)
            elif ch.kind == Channel.Kind.TEAMS_CHAT:
                ok = teams_chat_adapter.validate_config(cfg)
            else:
                ok = False
            if not ok:
                bad.append(ch.slug)

        details["channels_checked"] = len(channels)
        details["invalid_slugs"] = bad

        if bad:
            return (
                HealthStatus.DEGRADED,
                f"Channels with incomplete config: {', '.join(bad)}",
                details,
            )

        return HealthStatus.HEALTHY, "Voice operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Voice check failed: {exc}", details
