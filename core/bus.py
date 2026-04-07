"""
Circulatory Event Bus — The Heart of HumanOS.

All organ-to-organ communication flows through this bus. Organs NEVER
call each other directly. They emit events and subscribe to events.

Backed by Redis Streams for durability and consumer groups.
Falls back to an in-memory bus when Redis is unavailable (development).
"""

import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Callable
from datetime import datetime, timezone

logger = logging.getLogger("humanos.bus")


@dataclass
class Event:
    """A single event flowing through the circulatory system."""

    type: str
    source_organ: str
    payload: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: f"evt-{int(time.time() * 1000)}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class EventBus(ABC):
    """Abstract event bus — the port. Concrete adapters below."""

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Pump an event into the circulatory system."""

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Register a handler for a specific event type."""

    @abstractmethod
    def start_consuming(self) -> None:
        """Start the heart — begin pumping events to subscribers."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the heart gracefully."""


class InMemoryBus(EventBus):
    """
    In-memory event bus for development and testing.
    Events are dispatched synchronously — no Redis needed.
    """

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._history: list[Event] = []
        self._running = False

    def publish(self, event: Event) -> None:
        self._history.append(event)
        logger.info("BUS [%s] from %s: %s", event.type, event.source_organ, event.event_id)
        for handler in self._handlers.get(event.type, []):
            try:
                handler(event)
            except Exception:
                logger.exception("Handler failed for event %s", event.event_id)
        # Wildcard subscribers (subscribe to "*")
        for handler in self._handlers.get("*", []):
            try:
                handler(event)
            except Exception:
                logger.exception("Wildcard handler failed for event %s", event.event_id)

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug("Subscribed to '%s': %s", event_type, handler.__qualname__)

    def start_consuming(self) -> None:
        self._running = True
        logger.info("InMemoryBus started (synchronous mode)")

    def stop(self) -> None:
        self._running = False
        logger.info("InMemoryBus stopped")

    @property
    def history(self) -> list[Event]:
        return list(self._history)


class RedisBus(EventBus):
    """
    Production event bus backed by Redis Streams.
    Each organ gets its own consumer group for reliable delivery.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", stream: str = "humanos:events"):
        self._redis_url = redis_url
        self._stream = stream
        self._handlers: dict[str, list[Callable]] = {}
        self._running = False
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            import redis
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def publish(self, event: Event) -> None:
        r = self._get_redis()
        data = {"data": json.dumps(event.to_dict())}
        r.xadd(self._stream, data, maxlen=10000)
        logger.info("BUS [%s] from %s: %s", event.type, event.source_organ, event.event_id)

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def start_consuming(self, group: str = "humanos-workers", consumer: str = "worker-1"):
        r = self._get_redis()
        try:
            r.xgroup_create(self._stream, group, id="0", mkstream=True)
        except Exception:
            pass  # Group already exists

        self._running = True
        logger.info("RedisBus consuming stream=%s group=%s", self._stream, group)

        while self._running:
            try:
                messages = r.xreadgroup(group, consumer, {self._stream: ">"}, count=10, block=1000)
                for _, entries in messages:
                    for msg_id, fields in entries:
                        raw = json.loads(fields.get("data", "{}"))
                        event = Event.from_dict(raw)
                        for handler in self._handlers.get(event.type, []):
                            try:
                                handler(event)
                            except Exception:
                                logger.exception("Handler failed for %s", event.event_id)
                        for handler in self._handlers.get("*", []):
                            try:
                                handler(event)
                            except Exception:
                                logger.exception("Wildcard handler failed for %s", event.event_id)
                        r.xack(self._stream, group, msg_id)
            except Exception:
                logger.exception("RedisBus consume error, retrying...")
                time.sleep(1)

    def stop(self) -> None:
        self._running = False
        if self._redis:
            self._redis.close()
            self._redis = None
        logger.info("RedisBus stopped")


# Global bus instance — set during startup
_bus: EventBus | None = None


def get_bus() -> EventBus:
    """Get the global event bus instance."""
    global _bus
    if _bus is None:
        _bus = InMemoryBus()
        logger.info("Initialized default InMemoryBus")
    return _bus


def set_bus(bus: EventBus) -> None:
    """Set the global event bus (called during Django startup)."""
    global _bus
    _bus = bus


def emit(event_type: str, source_organ: str, payload: dict | None = None) -> Event:
    """Convenience function to emit an event."""
    event = Event(type=event_type, source_organ=source_organ, payload=payload or {})
    get_bus().publish(event)
    return event
