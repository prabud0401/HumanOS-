"""
Reproductive DNA — Template repository and clone defaults.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class ReproductiveDNA:
    template_repo: str
    default_branch: str
    clone_path: str
    auto_configure: bool


def get_reproductive_dna() -> ReproductiveDNA:
    raw = getattr(get_dna(), "_raw", {}) or {}
    rep = raw.get("reproductive")
    if not isinstance(rep, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            rep = organs.get("reproductive", {})
        if not isinstance(rep, dict):
            rep = {}
    return ReproductiveDNA(
        template_repo=str(rep.get("template_repo", "")),
        default_branch=str(rep.get("default_branch", "main")),
        clone_path=str(rep.get("clone_path", "./clones")),
        auto_configure=bool(rep.get("auto_configure", True)),
    )
