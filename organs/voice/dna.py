"""
Voice DNA — `organs.voice` in identity.yaml.
"""

from dataclasses import dataclass
from typing import Any

from core.dna_loader import get_dna


@dataclass
class VoiceDNA:
    default_channel: str
    notification_cooldown: int  # seconds between duplicate-route sends
    escalation_rules: list[dict[str, Any]]


def _section() -> dict:
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    organs = raw.get("organs") or {}
    if not isinstance(organs, dict):
        return {}
    sec = organs.get("voice") or {}
    return sec if isinstance(sec, dict) else {}


def get_voice_dna() -> VoiceDNA:
    s = _section()
    rules = s.get("escalation_rules") or []
    if not isinstance(rules, list):
        rules = []
    return VoiceDNA(
        default_channel=str(s.get("default_channel", "default")),
        notification_cooldown=int(s.get("notification_cooldown", 60)),
        escalation_rules=[r for r in rules if isinstance(r, dict)],
    )
