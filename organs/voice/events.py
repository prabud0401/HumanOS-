"""
Voice Events — outbound notifications driven by decisions and lifecycle signals.
"""

import logging

from core.bus import Event

logger = logging.getLogger("humanos.voice.events")

PUBLISHES = [
    "notification.sent",
    "notification.failed",
]

SUBSCRIBES = [
    "decision.made",
    "task.completed",
    "alert.triggered",
]


def handle_event(event: Event) -> None:
    if event.type not in SUBSCRIBES:
        return
    from .services import get_voice_service

    logger.info("Voice handling %s from %s", event.type, event.source_organ)
    get_voice_service().notify_from_event(event)
