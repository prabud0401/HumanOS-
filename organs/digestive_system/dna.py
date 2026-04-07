"""
Digestive System DNA — Supported formats, size limits, NLP model, extraction rules.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class DigestiveSystemDNA:
    supported_formats: list[str]
    max_file_size: int
    nlp_model: str
    extraction_rules: dict


def get_digestive_system_dna() -> DigestiveSystemDNA:
    dna = get_dna()
    fmts = dna.get("organs.digestive_system.supported_formats", ["vtt", "srt", "pdf", "eml"])
    if not isinstance(fmts, list):
        fmts = ["vtt", "srt", "pdf", "eml"]

    mfs = dna.get("organs.digestive_system.max_file_size", 50 * 1024 * 1024)
    try:
        mfs = int(mfs)
    except (TypeError, ValueError):
        mfs = 50 * 1024 * 1024

    nlp = str(dna.get("organs.digestive_system.nlp_model", "stub"))
    rules = dna.get("organs.digestive_system.extraction_rules", {})
    if not isinstance(rules, dict):
        rules = {}

    return DigestiveSystemDNA(
        supported_formats=[str(f).lower() for f in fmts],
        max_file_size=max(1024, mfs),
        nlp_model=nlp,
        extraction_rules=rules,
    )
