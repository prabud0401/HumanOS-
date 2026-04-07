"""
Git-based clone adapter — ``git clone`` from template repository.
"""

from __future__ import annotations

import json
import logging
import subprocess
import uuid
from pathlib import Path
from typing import Any

from ..dna import get_reproductive_dna
from ..models import CloneInstance
from ..ports import ClonePort, CloneSpec

logger = logging.getLogger("humanos.reproductive.git")


class GitCloneAdapter(ClonePort):
    """Materialize twins by cloning the template repo."""

    def create_clone(self, spec: CloneSpec) -> str:
        dna = get_reproductive_dna()
        repo = dna.template_repo
        if not repo:
            raise ValueError("template_repo not set in DNA")

        clone_id = f"clone-{uuid.uuid4().hex[:12]}"
        target = Path(spec.target_path) / spec.name
        target.parent.mkdir(parents=True, exist_ok=True)
        branch = spec.branch or dna.default_branch

        cmd = ["git", "clone", "--branch", branch, repo, str(target)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
            logger.exception("git clone failed")
            CloneInstance.objects.create(
                clone_id=clone_id,
                name=spec.name,
                status=CloneInstance.Status.FAILED,
                path=str(target),
                metadata={"error": str(exc)},
            )
            raise

        CloneInstance.objects.create(
            clone_id=clone_id,
            name=spec.name,
            status=CloneInstance.Status.READY,
            path=str(target),
            metadata={"repo": repo, "branch": branch},
        )
        return clone_id

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not config.get("identity", {}).get("name"):
            errors.append("identity.name required")
        if config.get("security", {}).get("encryption_key") in (None, ""):
            errors.append("security.encryption_key recommended")
        return len(errors) == 0, errors

    def export_template(self, output_path: str) -> str:
        dna = get_reproductive_dna()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        bundle = {"template_repo": dna.template_repo, "branch": dna.default_branch}
        path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        return str(path.resolve())
