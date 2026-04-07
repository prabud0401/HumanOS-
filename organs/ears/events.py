"""
Ears Events — publishes detections; accepts listener configuration commands.
"""

import logging
import uuid

from core.bus import Event, emit

logger = logging.getLogger("humanos.ears.events")

PUBLISHES = [
    "meeting.detected",
    "calendar.event",
    "message.received",
]

SUBSCRIBES = [
    "listener.configure",
]


def handle_event(event: Event) -> None:
    if event.type != "listener.configure":
        logger.debug("Ears ignoring non-config event %s", event.type)
        return
    _on_listener_configure(event)


def _on_listener_configure(event: Event) -> None:
    from .models import Listener
    from .services import get_ears_service

    payload = event.payload or {}
    name = payload.get("name", "")
    if not name:
        logger.error("listener.configure missing name")
        return
    kind = payload.get("kind", Listener.Kind.WEBHOOK_GENERIC)
    config = payload.get("config") or {}
    listener, _ = Listener.objects.update_or_create(
        name=name,
        defaults={"kind": kind, "config": config, "is_active": payload.get("is_active", True)},
    )
    logger.info("Listener configured: %s", listener.name)
    get_ears_service().refresh_listener_cache(listener)


def publish_meeting_detected(
    *,
    provider: str,
    meeting_id: str,
    title: str = "",
    join_url: str = "",
    extra: dict | None = None,
) -> str:
    eid = f"det-{uuid.uuid4().hex[:12]}"
    emit(
        "meeting.detected",
        "ears",
        payload={
            "detection_id": eid,
            "provider": provider,
            "meeting_id": meeting_id,
            "title": title,
            "join_url": join_url,
            **(extra or {}),
        },
    )
    return eid
