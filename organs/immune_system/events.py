"""
Immune System Events — Reacts to auth requests and cross-organ failure signals.
"""

import logging
import uuid

from core.bus import Event

from .ports import ThreatSignal
from .services import get_immune_system_service

logger = logging.getLogger("humanos.immune.events")

PUBLISHES = [
    "threat.detected",
    "access.denied",
    "key.rotated",
]

SUBSCRIBES = [
    "*.failed",
    "auth.requested",
]


def handle_event(event: Event) -> None:
    if event.type == "auth.requested":
        _on_auth_requested(event)
    elif event.type in (
        "task.failed",
        "processing.failed",
        "decision.failed",
        "transport.failed",
    ):
        _on_failure(event)
    else:
        logger.debug("Immune: no-op for event %s", event.type)


def _on_auth_requested(event: Event) -> None:
    p = event.payload or {}
    subject = p.get("subject", "")
    action = p.get("action", "access")
    resource = p.get("resource", "*")
    svc = get_immune_system_service()
    svc.can(subject, action, resource, p.get("context", {}))


def _on_failure(event: Event) -> None:
    """Elevate repeated failures toward threat detection."""
    p = event.payload or {}
    score = float(p.get("threat_score", 0.55))
    svc = get_immune_system_service()
    svc.evaluate_threat(
        ThreatSignal(
            source=event.source_organ,
            kind=event.type,
            score=score,
            evidence={"event_id": event.event_id, "payload": p},
        )
    )
