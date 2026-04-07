"""
Docker-based clone adapter — build/run a twin from a Dockerfile template path.
"""

from __future__ import annotations

import logging
import subprocess
import uuid
from pathlib import Path
from typing import Any

from ..models import CloneInstance
from ..ports import ClonePort, CloneSpec

logger = logging.getLogger("humanos.reproductive.docker")


class DockerCloneAdapter(ClonePort):
    """Provision clones as containers (requires Docker CLI)."""

    def __init__(self, dockerfile_dir: str | None = None, image_tag: str = "humanos-twin:latest"):
        self._dockerfile_dir = dockerfile_dir
        self._image_tag = image_tag

    def create_clone(self, spec: CloneSpec) -> str:
        clone_id = f"dock-{uuid.uuid4().hex[:12]}"
        ctx = Path(spec.target_path)
        ctx.mkdir(parents=True, exist_ok=True)
        docker_dir = Path(self._dockerfile_dir) if self._dockerfile_dir else ctx
        container_name = f"twin-{spec.name[:40].replace(' ', '-')}-{clone_id[:6]}"

        try:
            subprocess.run(
                ["docker", "build", "-t", self._image_tag, str(docker_dir)],
                check=True,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    container_name,
                    self._image_tag,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
            logger.exception("docker clone failed")
            CloneInstance.objects.create(
                clone_id=clone_id,
                name=spec.name,
                status=CloneInstance.Status.FAILED,
                path=str(ctx),
                metadata={"error": str(exc)},
            )
            raise

        CloneInstance.objects.create(
            clone_id=clone_id,
            name=spec.name,
            status=CloneInstance.Status.READY,
            path=str(ctx),
            metadata={"container": container_name, "image": self._image_tag},
        )
        return clone_id

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        errs: list[str] = []
        if not config.get("docker", {}).get("base_image"):
            errs.append("docker.base_image recommended")
        return len(errs) == 0, errs

    def export_template(self, output_path: str) -> str:
        p = Path(output_path)
        p.write_text(f"# Dockerfile export placeholder\n# Tag: {self._image_tag}\n", encoding="utf-8")
        return str(p.resolve())
