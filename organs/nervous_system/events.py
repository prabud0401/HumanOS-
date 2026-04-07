"""
Nervous System Events — Relays bus traffic to connected real-time clients.

SUBSCRIBES uses "*" so the in-memory bus invokes this handler for every event.
"""

import logging

from core.bus import Event

from .services import get_nervous_system_service

logger = logging.getLogger("humanos.nervous.events")

PUBLISHES = [
    "signal.broadcast",
    "connection.opened",
    "connection.closed",
]

SUBSCRIBES = [
    "*",
]


def handle_event(event: Event) -> None:
    """Forward bus events to WebSocket/SSE subscribers."""
    if event.source_organ == "nervous_system" and event.type == "signal.broadcast":
        return

    try:
        svc = get_nervous_system_service()
        svc.relay_bus_event(
            event.type,
            event.source_organ,
            {
                "payload": event.payload,
                "event_id": event.event_id,
                "timestamp": event.timestamp,
            },
        )
    except Exception:
        logger.exception("Failed to relay event %s", event.type)
