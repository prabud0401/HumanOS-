"""
Heart Ports — Abstract event bus surface (publish, subscribe, replay).
"""

from abc import ABC, abstractmethod
from collections.abc import Callable

from core.bus import Event


class EventBusPort(ABC):
    """
    Port for the circulatory event system.

    Concrete adapters back this with Redis Streams, in-memory queues, or tests.
    """

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Pump an event into the bus (and durable stream if applicable)."""

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """
        Register a handler. Use event_type '*' for wildcard delivery
        (same semantics as core.bus.InMemoryBus).
        """

    @abstractmethod
    def replay(
        self,
        *,
        start_after_id: str | None = None,
        limit: int = 500,
    ) -> list[Event]:
        """
        Return historical events for audit, debugging, or slow-consumer catch-up.

        Adapter-specific cursor: for Redis this may be a stream ID; for memory, opaque.
        """
