"""
WebSocket adapter — SignalPort backed by Django Channels group_send.

Falls back to in-memory dispatch when channels is not configured.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable

from ..ports import Envelope, SignalPort

logger = logging.getLogger("humanos.nervous.adapters.websocket")


class WebSocketSignalAdapter(SignalPort):
    def __init__(self):
        self._local_subs: dict[str, list[tuple[str, Callable[[Envelope], None]]]] = defaultdict(list)
        self._sub_seq = 0

    def broadcast(self, envelope: Envelope) -> int:
        group = f"ch_{envelope.channel}"
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.group_send)(
                    group,
                    {
                        "type": "humanos.event",
                        "event_type": envelope.event_type,
                        "payload": envelope.payload,
                    },
                )
                return -1  # unknown count from layer
        except Exception as exc:
            logger.debug("Channel layer unavailable (%s) — using local fan-out", exc)

        count = 0
        for _, cb in self._local_subs.get(envelope.channel, []):
            try:
                cb(envelope)
                count += 1
            except Exception:
                logger.exception("Local WS subscriber failed")
        return count

    def send_to(self, connection_id: str, envelope: Envelope) -> bool:
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.send)(
                    connection_id,
                    {
                        "type": "humanos.event",
                        "event_type": envelope.event_type,
                        "payload": envelope.payload,
                    },
                )
                return True
        except Exception as exc:
            logger.debug("Direct channel send failed: %s", exc)
        return False

    def subscribe_channel(self, channel: str, callback: Callable[[Envelope], None]) -> str:
        self._sub_seq += 1
        sid = f"sub-{self._sub_seq}"
        self._local_subs[channel].append((sid, callback))
        return sid
