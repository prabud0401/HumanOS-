"""
Heart DNA — organ-specific config from identity.yaml (`organs.heart`).
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class HeartDNA:
    heartbeat_interval: int  # seconds
    max_event_age: int  # seconds; events older may be trimmed / ignored in replay UI
    stream_name: str
    redis_url: str


def _organ_section() -> dict:
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    organs = raw.get("organs") or {}
    if not isinstance(organs, dict):
        return {}
    section = organs.get("heart") or {}
    return section if isinstance(section, dict) else {}


def get_heart_dna() -> HeartDNA:
    h = _organ_section()
    connections = (get_dna()._raw.get("connections") or {}) if hasattr(get_dna(), "_raw") else {}
    if not isinstance(connections, dict):
        connections = {}
    default_redis = (
        (connections.get("redis") or {}).get("url")
        if isinstance(connections.get("redis"), dict)
        else None
    ) or "redis://localhost:6379/0"

    return HeartDNA(
        heartbeat_interval=int(h.get("heartbeat_interval", 30)),
        max_event_age=int(h.get("max_event_age", 86400)),
        stream_name=str(h.get("stream_name", "humanos:events")),
        redis_url=str(h.get("redis_url", default_redis)),
    )
