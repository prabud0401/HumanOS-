"""
In-memory EventBusPort — development and tests (no Redis required).
"""

from __future__ import annotations

import json
import logging
from collections import deque
from collections.abc import Callable
from typing import Any

from core.bus import Event

from ..ports import EventBusPort

logger = logging.getLogger("humanos.heart.adapters.memory")


class MemoryEventBusAdapter(EventBusPort):
    """Bounded in-memory stream with synchronous dispatch to handlers."""

    def __init__(self, max_history: int = 10_000):
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}
        self._history: deque[dict[str, Any]] = deque(maxlen=max_history)
        self._seq = 0

    def publish(self, event: Event) -> None:
        self._seq += 1
        entry = {"id": f"mem-{self._seq}", "data": event.to_dict()}
        self._history.append(entry)
        self._dispatch(event)

    def _dispatch(self, event: Event) -> None:
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

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug("Memory bus subscribed %s -> %s", event_type, handler.__qualname__)

    def replay(
        self,
        *,
        start_after_id: str | None = None,
        limit: int = 500,
    ) -> list[Event]:
        items = list(self._history)
        if start_after_id:
            found = False
            filtered: list[dict[str, Any]] = []
            for entry in items:
                if found:
                    filtered.append(entry)
                elif entry["id"] == start_after_id:
                    found = True
            items = filtered
        out: list[Event] = []
        for entry in items[-limit:]:
            raw = entry.get("data") or {}
            if isinstance(raw, str):
                raw = json.loads(raw)
            out.append(Event.from_dict(raw))
        return out
