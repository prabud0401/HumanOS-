"""
Skeleton Events — Project lifecycle and configuration changes.
"""

import logging

from core.bus import Event

from .dna import get_skeleton_dna
from .models import Project
from .services import get_skeleton_service

logger = logging.getLogger("humanos.skeleton.events")

PUBLISHES = [
    "project.created",
    "config.changed",
]

SUBSCRIBES = [
    "project.requested",
]


def handle_event(event: Event) -> None:
    if event.type == "project.requested":
        _on_project_requested(event)
    else:
        logger.warning("Skeleton received unhandled event type: %s", event.type)


def _on_project_requested(event: Event) -> None:
    p = event.payload or {}
    slug = p.get("slug")
    if not slug:
        logger.error("project.requested missing slug")
        return
    svc = get_skeleton_service()
    name = p.get("name", slug)
    dna = get_skeleton_dna()
    root = p.get("root_path") or str(dna.project_root / slug)
    kind = p.get("kind", Project.Kind.APP)
    template_key = p.get("template_key")

    svc.create_project_record(slug=slug, name=name, root_path=root, kind=kind)
    svc.scaffold_project(slug, template_key, p.get("variables", {}))
