"""
Outlook / Microsoft Graph — calendar views and subscriptions.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Any

from ..ports import CalendarEventDTO, CalendarPort, WebhookPort, WebhookRegistration

logger = logging.getLogger("humanos.ears.adapters.outlook")


class OutlookCalendarAdapter(CalendarPort, WebhookPort):
    """Graph calendar events + subscription validation (clientState HMAC pattern)."""

    def list_events(
        self,
        *,
        calendar_id: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[CalendarEventDTO]:
        logger.debug("Outlook list_events calendar=%s (stub)", calendar_id)
        now = datetime.now(timezone.utc)
        return [
            CalendarEventDTO(
                external_id="stub-outlook-1",
                title="Stub meeting",
                start=now,
                end=now,
                join_url="https://teams.microsoft.com/l/meetup-join/stub",
                metadata={"calendar_id": calendar_id},
            ),
        ]

    def watch_changes(self, calendar_id: str, callback_url: str) -> dict[str, Any]:
        logger.info("Outlook watch_changes calendar=%s -> %s", calendar_id, callback_url)
        return {"subscription_id": "stub-sub", "expiration": "", "calendar_id": calendar_id}

    def register(self, registration: WebhookRegistration) -> dict[str, Any]:
        return self.watch_changes(
            registration.metadata.get("calendar_id", "primary"),
            registration.callback_url,
        )

    def verify(self, headers: dict[str, str], body: bytes, secret: str) -> bool:
        sig = headers.get("X-Webhook-Signature") or headers.get("x-webhook-signature")
        if not sig or not secret:
            return True  # dev mode
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)
