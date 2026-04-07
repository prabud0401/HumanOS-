"""
Nervous System Service — Relay bus events to WebSocket/SSE adapters.
"""

from __future__ import annotations

import fnmatch
import logging
import uuid

from django.db import transaction
from django.utils import timezone as dj_tz

from core.bus import emit

from .dna import get_nervous_system_dna
from .models import Connection
from .ports import Envelope, SignalPort
from .adapters.sse_adapter import SSESignalAdapter
from .adapters.websocket_adapter import WebSocketSignalAdapter

logger = logging.getLogger("humanos.nervous.services")


class CompositeSignalPort(SignalPort):
    """Try WebSocket groups first, then mirror to SSE queues."""

    def __init__(self, ws: SignalPort, sse: SignalPort):
        self._ws = ws
        self._sse = sse

    def broadcast(self, envelope: Envelope) -> int:
        a = self._ws.broadcast(envelope)
        b = self._sse.broadcast(envelope)
        if a < 0:
            return max(b, 1) if b else 1
        return a + b

    def send_to(self, connection_id: str, envelope: Envelope) -> bool:
        return self._ws.send_to(connection_id, envelope) or self._sse.send_to(connection_id, envelope)

    def subscribe_channel(self, channel: str, callback):
        self._ws.subscribe_channel(channel, callback)
        return self._sse.subscribe_channel(channel, callback)


class NervousSystemService:
    def __init__(self, port: SignalPort | None = None):
        self._port = port or CompositeSignalPort(WebSocketSignalAdapter(), SSESignalAdapter())

    def channel_allowed(self, channel: str) -> bool:
        dna = get_nervous_system_dna()
        for pattern in dna.allowed_channels:
            if pattern == "*" or fnmatch.fnmatch(channel, pattern):
                return True
        return False

    def open_connection(
        self,
        *,
        transport: str,
        channels: list[str],
        remote_addr: str | None = None,
        user_agent: str = "",
    ) -> Connection:
        dna = get_nervous_system_dna()
        open_count = Connection.objects.filter(state=Connection.State.OPEN).count()
        if open_count >= dna.max_connections:
            raise RuntimeError("max_connections exceeded")

        for ch in channels:
            if not self.channel_allowed(ch):
                raise PermissionError(f"channel not allowed: {ch}")

        cid = f"conn-{uuid.uuid4().hex[:12]}"
        with transaction.atomic():
            c = Connection.objects.create(
                connection_id=cid,
                transport=transport,
                remote_addr=remote_addr,
                user_agent=user_agent[:512],
                subscribed_channels=channels,
                state=Connection.State.OPEN,
                last_heartbeat=dj_tz.now(),
            )
        emit(
            "connection.opened",
            "nervous_system",
            payload={"connection_id": cid, "transport": transport, "channels": channels},
        )
        return c

    def close_connection(self, connection_id: str) -> None:
        Connection.objects.filter(connection_id=connection_id).update(
            state=Connection.State.CLOSED,
            closed_at=dj_tz.now(),
        )
        emit(
            "connection.closed",
            "nervous_system",
            payload={"connection_id": connection_id},
        )

    def relay_bus_event(self, event_type: str, source_organ: str, payload: dict) -> None:
        channel = f"bus.{source_organ}"
        if not self.channel_allowed(channel) and not self.channel_allowed("*"):
            return
        env = Envelope(channel=channel, event_type=event_type, payload=payload)
        n = self._port.broadcast(env)
        emit(
            "signal.broadcast",
            "nervous_system",
            payload={"channel": channel, "event_type": event_type, "deliveries": n},
        )

    def touch_heartbeat(self, connection_id: str) -> None:
        Connection.objects.filter(connection_id=connection_id).update(last_heartbeat=dj_tz.now())

    def publish_envelope(self, envelope: Envelope) -> int:
        """Direct broadcast without wrapping as a bus relay (for tasks/admin APIs)."""
        return self._port.broadcast(envelope)


_service: NervousSystemService | None = None


def get_nervous_system_service() -> NervousSystemService:
    global _service
    if _service is None:
        _service = NervousSystemService()
    return _service
