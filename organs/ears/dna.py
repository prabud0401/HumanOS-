"""
Ears DNA — `organs.ears` in identity.yaml.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class EarsDNA:
    poll_interval: int  # seconds
    watched_calendars: list[str]
    webhook_secret: str


def _section() -> dict:
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    organs = raw.get("organs") or {}
    if not isinstance(organs, dict):
        return {}
    sec = organs.get("ears") or {}
    return sec if isinstance(sec, dict) else {}


def get_ears_dna() -> EarsDNA:
    s = _section()
    cals = s.get("watched_calendars") or []
    if not isinstance(cals, list):
        cals = []
    return EarsDNA(
        poll_interval=int(s.get("poll_interval", 120)),
        watched_calendars=[str(x) for x in cals],
        webhook_secret=str(s.get("webhook_secret", "")),
    )
