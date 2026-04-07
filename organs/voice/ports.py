"""
Voice Ports — outbound notifications and channel connectivity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutboundMessage:
    subject: str = ""
    body: str = ""
    recipient: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SendResult:
    ok: bool
    provider_message_id: str = ""
    error: str = ""


class NotificationPort(ABC):
    """Send one or many outbound messages through configured channels."""

    @abstractmethod
    def send(self, channel_slug: str, message: OutboundMessage) -> SendResult:
        """Deliver a single message."""

    @abstractmethod
    def send_batch(self, channel_slug: str, messages: list[OutboundMessage]) -> list[SendResult]:
        """Deliver multiple messages (adapters may batch API calls)."""


class ChannelPort(ABC):
    """Validate channel configuration and connectivity."""

    @abstractmethod
    def connect(self, config: dict[str, Any]) -> dict[str, Any]:
        """Return normalized status / handles after validating config."""

    @abstractmethod
    def validate(self, config: dict[str, Any]) -> bool:
        """Return True if required keys are present and well-formed."""
