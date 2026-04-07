"""
Nervous System DNA — Connection limits, heartbeat, allowed channels.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class NervousSystemDNA:
    max_connections: int
    heartbeat_interval: int
    allowed_channels: list[str]


def get_nervous_system_dna() -> NervousSystemDNA:
    dna = get_dna()
    max_c = dna.get("organs.nervous_system.max_connections", 1000)
    try:
        max_c = int(max_c)
    except (TypeError, ValueError):
        max_c = 1000

    hb = dna.get("organs.nervous_system.heartbeat_interval", 30)
    try:
        hb = int(hb)
    except (TypeError, ValueError):
        hb = 30

    ch = dna.get("organs.nervous_system.allowed_channels", ["*"])
    if not isinstance(ch, list):
        ch = ["*"]

    return NervousSystemDNA(
        max_connections=max(1, max_c),
        heartbeat_interval=max(5, hb),
        allowed_channels=[str(x) for x in ch],
    )
