"""
Skeleton Service — Local ProjectPort / TemplatePort orchestration.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from django.db import transaction

from core.bus import emit

from .dna import get_skeleton_dna
from .models import ConfigEntry, Project, ProjectTemplate
from .ports import (
    ProjectPort,
    ScaffoldRequest,
    ScaffoldResult,
    StructureReport,
    TemplateDescriptor,
    TemplatePort,
)

logger = logging.getLogger("humanos.skeleton.services")


class LocalProjectPort(ProjectPort):
    def scaffold(self, request: ScaffoldRequest) -> ScaffoldResult:
        dna = get_skeleton_dna()
        request.target_root.mkdir(parents=True, exist_ok=True)
        created: list[str] = [str(request.target_root)]
        try:
            if request.template_key:
                tmpl = LocalTemplatePort()
                res = tmpl.apply(request.template_key, request.target_root, request.variables)
                if not res.success:
                    return res
                created.extend(res.created_paths)
            emit(
                "project.created",
                "skeleton",
                payload={"slug": request.project_slug, "paths": created},
            )
            return ScaffoldResult(True, "Scaffold complete", created_paths=created)
        except Exception as exc:
            logger.exception("scaffold failed")
            return ScaffoldResult(False, str(exc), created_paths=created)

    def validate_structure(self, project_root: Path, expected_layout: dict[str, Any]) -> StructureReport:
        required = expected_layout.get("required_dirs", [])
        required_files = expected_layout.get("required_files", [])
        missing: list[str] = []
        for rel in required:
            p = project_root / rel
            if not p.is_dir():
                missing.append(str(rel))
        for rel in required_files:
            p = project_root / rel
            if not p.is_file():
                missing.append(str(rel))
        return StructureReport(valid=len(missing) == 0, missing=missing)


class LocalTemplatePort(TemplatePort):
    def list_templates(self) -> list[TemplateDescriptor]:
        by_key: dict[str, TemplateDescriptor] = {}
        for row in ProjectTemplate.objects.order_by("key", "-version"):
            if row.key in by_key:
                continue
            by_key[row.key] = TemplateDescriptor(
                key=row.key,
                label=row.label,
                version=row.version,
                path=Path(row.source_path),
            )
        return list(by_key.values())

    def apply(self, template_key: str, target: Path, variables: dict[str, Any]) -> ScaffoldResult:
        try:
            tmpl = ProjectTemplate.objects.get(key=template_key)
        except ProjectTemplate.DoesNotExist:
            dna = get_skeleton_dna()
            src = dna.template_dir / template_key
            if not src.is_dir():
                return ScaffoldResult(False, f"Unknown template: {template_key}")
            shutil.copytree(src, target, dirs_exist_ok=True)
            created = [str(p.relative_to(target)) for p in target.rglob("*") if p.is_file()]
            return ScaffoldResult(True, "Copied built-in template", created_paths=created)

        src = Path(tmpl.source_path)
        if not src.is_dir():
            return ScaffoldResult(False, f"Template path missing: {src}")
        shutil.copytree(src, target, dirs_exist_ok=True)
        created = [str(p.relative_to(target)) for p in target.rglob("*") if p.is_file()]
        return ScaffoldResult(True, f"Applied {template_key}", created_paths=created)


class SkeletonService:
    def __init__(self, project_port: ProjectPort | None = None, template_port: TemplatePort | None = None):
        self._project = project_port or LocalProjectPort()
        self._templates = template_port or LocalTemplatePort()

    def create_project_record(
        self,
        *,
        slug: str,
        name: str,
        root_path: str,
        kind: str = Project.Kind.APP,
    ) -> Project:
        with transaction.atomic():
            return Project.objects.create(slug=slug, name=name, root_path=root_path, kind=kind)

    def scaffold_project(self, slug: str, template_key: str | None, variables: dict[str, Any]) -> ScaffoldResult:
        dna = get_skeleton_dna()
        target = dna.project_root / slug
        req = ScaffoldRequest(project_slug=slug, template_key=template_key, target_root=target, variables=variables)
        return self._project.scaffold(req)

    def set_config(self, key: str, value: Any, *, project: Project | None = None) -> ConfigEntry:
        scope = ConfigEntry.Scope.PROJECT if project else ConfigEntry.Scope.GLOBAL
        obj, _ = ConfigEntry.objects.update_or_create(
            scope=scope,
            project=project,
            key=key,
            defaults={"value": value},
        )
        emit(
            "config.changed",
            "skeleton",
            payload={"key": key, "scope": scope, "project_slug": project.slug if project else None},
        )
        return obj


_service: SkeletonService | None = None


def get_skeleton_service() -> SkeletonService:
    global _service
    if _service is None:
        _service = SkeletonService()
    return _service
