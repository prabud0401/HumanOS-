"""
Google Calendar — events.list and channel watch.
"""

from __future__ import annotations

import hmac
import logging
from datetime import datetime, timezone
from typing import Any

from ..ports import CalendarEventDTO, CalendarPort, WebhookPort, WebhookRegistration

logger = logging.getLogger("humanos.ears.adapters.google_calendar")


class GoogleCalendarAdapter(CalendarPort, WebhookPort):
    """Calendar API + optional push notifications."""

    def list_events(
        self,
        *,
        calendar_id: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[CalendarEventDTO]:
        logger.debug("Google list_events calendar=%s (stub)", calendar_id)
        now = datetime.now(timezone.utc)
        return [
            CalendarEventDTO(
                external_id="stub-gcal-1",
                title="Stub Google Meet",
                start=now,
                end=now,
                join_url="https://meet.google.com/stub",
                metadata={"calendar_id": calendar_id},
            ),
        ]

    def watch_changes(self, calendar_id: str, callback_url: str) -> dict[str, Any]:
        logger.info("Google watch_changes calendar=%s -> %s", calendar_id, callback_url)
        return {"channel_id": "stub-channel", "resource_id": "stub-res", "calendar_id": calendar_id}

    def register(self, registration: WebhookRegistration) -> dict[str, Any]:
        cal = registration.metadata.get("calendar_id", "primary")
        return self.watch_changes(cal, registration.callback_url)

    def verify(self, headers: dict[str, str], body: bytes, secret: str) -> bool:
        token = headers.get("X-Goog-Channel-Token") or headers.get("x-goog-channel-token") or ""
        if not secret:
            return True
        if not token or len(token) != len(secret):
            return False
        return hmac.compare_digest(token.encode("utf-8"), secret.encode("utf-8"))
