"""
Reproductive events — clone requests and config export.
"""

import logging

from core.bus import Event
from core.dna_loader import get_dna

logger = logging.getLogger("humanos.reproductive.events")

PUBLISHES = [
    "clone.created",
    "clone.configured",
    "migration.complete",
]

SUBSCRIBES = [
    "clone.requested",
    "config.exported",
]


def handle_event(event: Event) -> None:
    handlers = {
        "clone.requested": _on_clone_requested,
        "config.exported": _on_config_exported,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Reproductive received unhandled event: %s", event.type)


def _on_clone_requested(event: Event) -> None:
    from .dna import get_reproductive_dna
    from .ports import CloneSpec
    from .services import get_reproductive_service

    p = event.payload or {}
    dna = get_reproductive_dna()
    spec = CloneSpec(
        name=p.get("name", "twin"),
        target_path=p.get("target_path", dna.clone_path),
        branch=p.get("branch", dna.default_branch),
        options=p.get("options") or {},
    )
    get_reproductive_service().create_clone(spec)


def _on_config_exported(event: Event) -> None:
    from .services import get_reproductive_service

    p = event.payload or {}
    cfg = p.get("config")
    if not isinstance(cfg, dict):
        cfg = get_dna_snapshot()
    clone_id = p.get("clone_id")
    get_reproductive_service().snapshot_config(clone_id, cfg)


def get_dna_snapshot() -> dict:
    """Serialize current DNA raw for export."""
    dna = get_dna()
    raw = getattr(dna, "_raw", {})
    return dict(raw) if isinstance(raw, dict) else {}
