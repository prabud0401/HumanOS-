"""
Immune System DNA — Crypto algorithm, token TTL, threat scoring, audit retention.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class ImmuneSystemDNA:
    encryption_algorithm: str
    token_ttl: int
    threat_threshold: float
    audit_retention_days: int


def get_immune_system_dna() -> ImmuneSystemDNA:
    dna = get_dna()
    algo = str(dna.get("organs.immune_system.encryption_algorithm", "fernet"))
    ttl = dna.get("organs.immune_system.token_ttl", 3600)
    try:
        ttl = int(ttl)
    except (TypeError, ValueError):
        ttl = 3600

    th = dna.get("organs.immune_system.threat_threshold", 0.7)
    try:
        th = float(th)
    except (TypeError, ValueError):
        th = 0.7

    ar = dna.get("organs.immune_system.audit_retention_days", 90)
    try:
        ar = int(ar)
    except (TypeError, ValueError):
        ar = 90

    return ImmuneSystemDNA(
        encryption_algorithm=algo,
        token_ttl=max(60, ttl),
        threat_threshold=max(0.0, min(1.0, th)),
        audit_retention_days=max(1, ar),
    )
