"""
Skeleton DNA — Project root, template directory, naming conventions.
"""

from dataclasses import dataclass
from pathlib import Path

from core.dna_loader import get_dna


@dataclass
class SkeletonDNA:
    project_root: Path
    template_dir: Path
    naming_conventions: dict


def get_skeleton_dna() -> SkeletonDNA:
    dna = get_dna()
    root = dna.get("organs.skeleton.project_root", "")
    tmpl = dna.get("organs.skeleton.template_dir", "")
    conventions = dna.get("organs.skeleton.naming_conventions", {})
    if not isinstance(conventions, dict):
        conventions = {"slug": "kebab-case", "python_module": "snake_case"}

    base = Path(__file__).resolve().parents[2]
    project_root = Path(root) if root else base
    template_dir = Path(tmpl) if tmpl else (project_root / "templates" / "projects")

    return SkeletonDNA(
        project_root=project_root,
        template_dir=template_dir,
        naming_conventions=conventions,
    )
