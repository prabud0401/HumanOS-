"""
Heart Events — Publishes lifecycle and pulse; subscribes to all traffic for audit.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from django.utils import dateparse

from core.bus import Event, emit

from .models import EventLog

logger = logging.getLogger("humanos.heart.events")

PUBLISHES = [
    "heartbeat.pulse",
    "system.startup",
    "system.shutdown",
]

SUBSCRIBES = [
    "*",
]


def _event_timestamp(event: Event) -> datetime:
    parsed = dateparse.parse_datetime(event.timestamp)
    if parsed is None:
        return datetime.now(timezone.utc)
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.utc)
    return parsed


def handle_event(event: Event) -> None:
    """
    Monitor every event on the bus: persist audit row (best-effort) and trace.
    """
    try:
        EventLog.objects.create(
            event_id=event.event_id,
            event_type=event.type,
            source_organ=event.source_organ,
            payload=event.payload,
            timestamp=_event_timestamp(event),
        )
    except Exception:
        logger.exception("Heart failed to persist EventLog for %s", event.event_id)

    logger.debug(
        "Heart observed [%s] from %s id=%s",
        event.type,
        event.source_organ,
        event.event_id,
    )


def emit_system_startup(payload: dict | None = None) -> None:
    emit("system.startup", "heart", payload=payload or {})


def emit_system_shutdown(payload: dict | None = None) -> None:
    emit("system.shutdown", "heart", payload=payload or {})
