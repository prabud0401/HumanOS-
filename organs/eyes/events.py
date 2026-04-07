"""
Eyes Events — dashboard analytics on the bus; listens for completion-style signals.
"""

import logging
import uuid

from core.bus import Event, emit

logger = logging.getLogger("humanos.eyes.events")

PUBLISHES = [
    "dashboard.viewed",
    "widget.interacted",
]

SUBSCRIBES = [
    "*.complete",
    "pulse.report",
]


def _relevant(event: Event) -> bool:
    if event.type == "pulse.report":
        return True
    if event.type.endswith(".complete"):
        return True
    return False


def handle_event(event: Event) -> None:
    if not _relevant(event):
        return
    logger.debug("Eyes updating internal state from %s", event.type)
    # Frontend cache invalidation / server-side aggregates would plug in here.
    emit(
        "widget.interacted",
        "eyes",
        payload={
            "interaction_id": f"wi-{uuid.uuid4().hex[:10]}",
            "cause_event": event.type,
            "source_event_id": event.event_id,
        },
    )
