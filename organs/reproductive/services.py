"""
Reproductive service — clone and migration orchestration.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from core.bus import emit

from .dna import get_reproductive_dna
from .models import CloneConfig, CloneInstance, MigrationLog
from .ports import ClonePort, CloneSpec, MigrationPlan, MigrationPort

logger = logging.getLogger("humanos.reproductive.services")


class OrmMigrationAdapter(MigrationPort):
    """Persists migration attempts; real schema changes are project-specific."""

    def migrate(self, plan: MigrationPlan) -> dict[str, Any]:
        MigrationLog.objects.create(
            plan_id=plan.plan_id,
            direction=MigrationLog.Direction.UP,
            success=True,
            detail={"steps": plan.steps},
        )
        return {"applied_steps": len(plan.steps), "plan_id": plan.plan_id}

    def rollback(self, plan: MigrationPlan) -> dict[str, Any]:
        MigrationLog.objects.create(
            plan_id=plan.plan_id,
            direction=MigrationLog.Direction.DOWN,
            success=True,
            detail={"steps": plan.steps},
        )
        return {"rolled_back_steps": len(plan.steps), "plan_id": plan.plan_id}


class ReproductiveService:
    def __init__(self, clone: ClonePort, migration: MigrationPort):
        self._clone = clone
        self._migration = migration

    def create_clone(self, spec: CloneSpec) -> str:
        clone_id = self._clone.create_clone(spec)
        emit("clone.created", "reproductive", payload={"clone_id": clone_id, "name": spec.name})
        return clone_id

    def snapshot_config(self, clone_id: str | None, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str)
        checksum = hashlib.sha256(raw.encode()).hexdigest()
        config_id = f"cfg-{checksum[:16]}"
        clone = CloneInstance.objects.filter(clone_id=clone_id).first() if clone_id else None
        CloneConfig.objects.create(config_id=config_id, clone=clone, payload=payload, checksum=checksum)
        emit("clone.configured", "reproductive", payload={"config_id": config_id})
        return config_id

    def run_migration(self, plan: MigrationPlan) -> dict[str, Any]:
        result = self._migration.migrate(plan)
        emit("migration.complete", "reproductive", payload=result)
        return result

    def rollback_migration(self, plan: MigrationPlan) -> dict[str, Any]:
        return self._migration.rollback(plan)

    def validate(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        return self._clone.validate_config(config)


_service: ReproductiveService | None = None


def _make_clone_port() -> ClonePort:
    dna = get_reproductive_dna()
    if dna.template_repo:
        from .adapters.git_adapter import GitCloneAdapter

        return GitCloneAdapter()
    from .adapters.docker_adapter import DockerCloneAdapter

    return DockerCloneAdapter(dockerfile_dir=dna.clone_path)


def get_reproductive_service() -> ReproductiveService:
    global _service
    if _service is None:
        _service = ReproductiveService(clone=_make_clone_port(), migration=OrmMigrationAdapter())
    return _service
