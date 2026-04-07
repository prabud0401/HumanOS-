"""
Eyes DNA — `organs.eyes` in identity.yaml.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class EyesDNA:
    theme: str
    refresh_interval: int  # seconds
    default_layout: list[str]  # ordered widget slugs


def _section() -> dict:
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    organs = raw.get("organs") or {}
    if not isinstance(organs, dict):
        return {}
    sec = organs.get("eyes") or {}
    return sec if isinstance(sec, dict) else {}


def get_eyes_dna() -> EyesDNA:
    s = _section()
    layout = s.get("default_layout") or ["summary", "meetings", "tasks"]
    if not isinstance(layout, list):
        layout = ["summary", "meetings", "tasks"]
    return EyesDNA(
        theme=str(s.get("theme", "dark")),
        refresh_interval=int(s.get("refresh_interval", 30)),
        default_layout=[str(x) for x in layout],
    )
