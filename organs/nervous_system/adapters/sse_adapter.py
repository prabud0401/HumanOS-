"""
Server-Sent Events adapter — queues envelopes per logical stream id.

HTTP layer consumes queues; this adapter implements SignalPort fan-out to those queues.
"""

from __future__ import annotations

import logging
import queue
import threading
from collections import defaultdict
from typing import Callable

from ..ports import Envelope, SignalPort

logger = logging.getLogger("humanos.nervous.adapters.sse")


class SSESignalAdapter(SignalPort):
    """In-process SSE fan-out using thread-safe queues per stream."""

    def __init__(self):
        self._lock = threading.Lock()
        self._queues: dict[str, list[queue.Queue]] = defaultdict(list)
        self._subs: dict[str, list[tuple[str, Callable[[Envelope], None]]]] = defaultdict(list)
        self._sub_seq = 0

    def register_stream(self, stream_id: str) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=256)
        with self._lock:
            self._queues[stream_id].append(q)
        return q

    def unregister_stream(self, stream_id: str, q: queue.Queue) -> None:
        with self._lock:
            if stream_id in self._queues:
                try:
                    self._queues[stream_id].remove(q)
                except ValueError:
                    pass

    def broadcast(self, envelope: Envelope) -> int:
        count = 0
        with self._lock:
            targets = list(self._queues.get(envelope.channel, []))
        for q in targets:
            try:
                q.put_nowait(envelope)
                count += 1
            except queue.Full:
                logger.warning("SSE queue full for channel %s", envelope.channel)
        for _, cb in self._subs.get(envelope.channel, []):
            try:
                cb(envelope)
                count += 1
            except Exception:
                logger.exception("SSE callback failed")
        return count

    def send_to(self, connection_id: str, envelope: Envelope) -> bool:
        with self._lock:
            targets = list(self._queues.get(connection_id, []))
        for q in targets:
            try:
                q.put_nowait(envelope)
                return True
            except queue.Full:
                continue
        return bool(targets)

    def subscribe_channel(self, channel: str, callback: Callable[[Envelope], None]) -> str:
        self._sub_seq += 1
        sid = f"sse-sub-{self._sub_seq}"
        self._subs[channel].append((sid, callback))
        return sid
