"""
Circulatory events — publishes delivery lifecycle; subscribes to data readiness.
"""

import logging

from core.bus import Event, emit

logger = logging.getLogger("humanos.circulatory.events")

PUBLISHES = [
    "data.delivered",
    "pipeline.completed",
    "transport.failed",
]

SUBSCRIBES = [
    "data.ready",
    "pipeline.trigger",
]


def handle_event(event: Event) -> None:
    """Route bus events into circulatory services."""
    handlers = {
        "data.ready": _on_data_ready,
        "pipeline.trigger": _on_pipeline_trigger,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Circulatory received unhandled event: %s", event.type)


def _on_data_ready(event: Event) -> None:
    from .services import get_circulatory_service

    logger.info("data.ready for packet context: %s", event.payload.get("packet_id", "n/a"))
    get_circulatory_service().on_data_ready(event)


def _on_pipeline_trigger(event: Event) -> None:
    from .services import get_circulatory_service

    logger.info("pipeline.trigger slug=%s", event.payload.get("pipeline_slug", "n/a"))
    get_circulatory_service().on_pipeline_trigger(event)


def publish_transport_failed(source: str, error: str, details: dict | None = None) -> None:
    emit("transport.failed", source, payload={"error": error, **(details or {})})
