"""
Ears Ports — calendar polling and webhook verification.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CalendarEventDTO:
    external_id: str
    title: str
    start: datetime
    end: datetime
    join_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookRegistration:
    listener_name: str
    callback_url: str
    secret: str
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CalendarPort(ABC):
    """List calendar events and establish change notifications."""

    @abstractmethod
    def list_events(
        self,
        *,
        calendar_id: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[CalendarEventDTO]:
        """Return events in the window (provider-specific paging handled in adapter)."""

    @abstractmethod
    def watch_changes(self, calendar_id: str, callback_url: str) -> dict[str, Any]:
        """Register a push channel or sync token; return provider handles."""


class WebhookPort(ABC):
    """Register and verify inbound HTTP webhooks."""

    @abstractmethod
    def register(self, registration: WebhookRegistration) -> dict[str, Any]:
        """Create subscription on provider side if applicable."""

    @abstractmethod
    def verify(self, headers: dict[str, str], body: bytes, secret: str) -> bool:
        """Validate authenticity (HMAC, signed token, etc.)."""
