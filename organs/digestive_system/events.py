"""
Digestive System Events — Ingest artifacts and raw data payloads.
"""

import logging

from core.bus import Event

from .services import get_digestive_system_service

logger = logging.getLogger("humanos.digestive.events")

PUBLISHES = [
    "knowledge.extracted",
    "processing.failed",
    "data.transformed",
]

SUBSCRIBES = [
    "artifacts.ingested",
    "data.received",
]


def handle_event(event: Event) -> None:
    if event.type == "artifacts.ingested":
        _on_artifacts_ingested(event)
    elif event.type == "data.received":
        _on_data_received(event)
    else:
        logger.warning("Digestive received unhandled event type: %s", event.type)


def _on_artifacts_ingested(event: Event) -> None:
    p = event.payload or {}
    uri = p.get("uri") or p.get("path")
    fmt = (p.get("format") or p.get("mime") or "vtt").lower()
    if not uri:
        logger.error("artifacts.ingested missing uri/path")
        return
    svc = get_digestive_system_service()
    svc.run_job(str(uri), fmt)


def _on_data_received(event: Event) -> None:
    p = event.payload or {}
    uri = p.get("uri") or p.get("path")
    fmt = (p.get("format") or "vtt").lower()
    if not uri:
        logger.error("data.received missing uri/path")
        return
    get_digestive_system_service().run_job(str(uri), fmt)
