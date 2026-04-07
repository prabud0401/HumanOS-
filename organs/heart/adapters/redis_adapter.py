"""
Redis Streams EventBusPort — production-durable event routing.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable

from core.bus import Event

from ..ports import EventBusPort

logger = logging.getLogger("humanos.heart.adapters.redis")


class RedisStreamEventBusAdapter(EventBusPort):
    """
    Publishes to a Redis stream and registers local handlers (dispatch is still
    driven by your process's consumer or by synchronous fan-out after XADD).
    """

    def __init__(self, redis_url: str, stream_name: str, maxlen: int = 50_000):
        self._redis_url = redis_url
        self._stream_name = stream_name
        self._maxlen = maxlen
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}
        self._redis = None

    def _client(self):
        if self._redis is None:
            import redis

            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def publish(self, event: Event) -> None:
        r = self._client()
        payload = json.dumps(event.to_dict())
        msg_id = r.xadd(
            self._stream_name,
            {"data": payload},
            maxlen=self._maxlen,
            approximate=True,
        )
        logger.debug("XADD %s -> %s", self._stream_name, msg_id)
        self._dispatch_local(event)

    def _dispatch_local(self, event: Event) -> None:
        for handler in self._handlers.get(event.type, []):
            try:
                handler(event)
            except Exception:
                logger.exception("Redis adapter local handler failed for %s", event.event_id)
        for handler in self._handlers.get("*", []):
            try:
                handler(event)
            except Exception:
                logger.exception("Redis adapter wildcard handler failed for %s", event.event_id)

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def replay(
        self,
        *,
        start_after_id: str | None = None,
        limit: int = 500,
    ) -> list[Event]:
        r = self._client()
        if start_after_id:
            entries = r.xrange(
                self._stream_name,
                min=f"({start_after_id}",
                max="+",
                count=limit,
            )
        else:
            entries = list(reversed(r.xrevrange(self._stream_name, count=limit)))
        out: list[Event] = []
        for _msg_id, fields in entries:
            raw = json.loads(fields.get("data", "{}"))
            out.append(Event.from_dict(raw))
        return out
