"""
Circulatory System DNA — Pipeline and transport settings from identity.yaml.

Reads ``circulatory`` (or nested ``organs.circulatory``) from raw DNA with defaults.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class CirculatoryDNA:
    max_packet_size: int
    compression: str
    retry_policy: str
    transport_mode: str


def get_circulatory_dna() -> CirculatoryDNA:
    """Extract circulatory-specific config from global DNA."""
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    circ = raw.get("circulatory")
    if not isinstance(circ, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            circ = organs.get("circulatory", {})
        if not isinstance(circ, dict):
            circ = {}
    return CirculatoryDNA(
        max_packet_size=int(circ.get("max_packet_size", 16 * 1024 * 1024)),
        compression=str(circ.get("compression", "none")),
        retry_policy=str(circ.get("retry_policy", "exponential_backoff")),
        transport_mode=str(circ.get("transport_mode", "async")),
    )
