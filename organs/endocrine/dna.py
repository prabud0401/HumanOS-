"""
Endocrine DNA — Scheduler tuning from identity.yaml.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class EndocrineDNA:
    timezone: str
    default_retry_count: int
    max_concurrent_jobs: int
    schedule_check_interval: int


def get_endocrine_dna() -> EndocrineDNA:
    raw = getattr(get_dna(), "_raw", {}) or {}
    endo = raw.get("endocrine")
    if not isinstance(endo, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            endo = organs.get("endocrine", {})
        if not isinstance(endo, dict):
            endo = {}
    identity = get_dna().identity
    return EndocrineDNA(
        timezone=str(endo.get("timezone", identity.timezone)),
        default_retry_count=int(endo.get("default_retry_count", 3)),
        max_concurrent_jobs=int(endo.get("max_concurrent_jobs", 8)),
        schedule_check_interval=int(endo.get("schedule_check_interval", 60)),
    )
