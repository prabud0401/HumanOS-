"""
Nervous System Ports — Signal broadcast and targeted delivery.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Envelope:
    """Wrapped message for a channel."""

    channel: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)


class SignalPort(ABC):
    """Port for fan-out to real-time transports."""

    @abstractmethod
    def broadcast(self, envelope: Envelope) -> int:
        """Send to all subscribers of the envelope's channel; returns delivery count."""

    @abstractmethod
    def send_to(self, connection_id: str, envelope: Envelope) -> bool:
        """Send to a single connection."""

    @abstractmethod
    def subscribe_channel(self, channel: str, callback: Callable[[Envelope], None]) -> str:
        """Register in-process subscriber; returns subscription id."""
