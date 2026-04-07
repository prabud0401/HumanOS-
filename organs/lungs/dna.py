"""
Lungs DNA — `organs.lungs` section in identity.yaml.
"""

from dataclasses import dataclass
from pathlib import Path

from core.dna_loader import get_dna


@dataclass
class LungsDNA:
    download_path: Path
    max_concurrent_downloads: int
    retry_count: int
    default_source: str


def _section() -> dict:
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    organs = raw.get("organs") or {}
    if not isinstance(organs, dict):
        return {}
    sec = organs.get("lungs") or {}
    return sec if isinstance(sec, dict) else {}


def get_lungs_dna() -> LungsDNA:
    s = _section()
    path = Path(s.get("download_path", "var/ingestion")).expanduser()
    return LungsDNA(
        download_path=path,
        max_concurrent_downloads=int(s.get("max_concurrent_downloads", 4)),
        retry_count=int(s.get("retry_count", 3)),
        default_source=str(s.get("default_source", "teams")),
    )
