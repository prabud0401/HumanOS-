"""
Heart Service Layer — bus adapters, replay, and heartbeat bookkeeping.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from core.bus import Event, emit, get_bus

from .dna import get_heart_dna
from .models import HeartbeatRecord
from .ports import EventBusPort

logger = logging.getLogger("humanos.heart.services")


class HeartService:
    """Orchestrates EventBusPort usage and heartbeat emission."""

    def __init__(self, port: EventBusPort | None = None):
        self._port = port
        self._dna = get_heart_dna()

    @property
    def stream_name(self) -> str:
        return self._dna.stream_name

    def replay_recent(self, *, start_after_id: str | None = None, limit: int = 200) -> list[Event]:
        bus = get_bus()
        if hasattr(bus, "history"):
            hist = list(bus.history)
            if start_after_id:
                idx = next(
                    (i for i, e in enumerate(hist) if e.event_id == start_after_id),
                    None,
                )
                if idx is not None:
                    hist = hist[idx + 1 :]
            return hist[-limit:]
        if self._port is not None:
            return self._port.replay(start_after_id=start_after_id, limit=limit)
        return []

    def record_pulse(self, *, pending_estimate: int = 0, wildcard_handlers: int = 0) -> HeartbeatRecord:
        dna = self._dna
        beat_id = f"hb-{uuid.uuid4().hex[:12]}"
        rec = HeartbeatRecord.objects.create(
            beat_id=beat_id,
            status=HeartbeatRecord.Status.OK,
            stream_name=dna.stream_name,
            pending_events_estimate=pending_estimate,
            subscribers_wildcard=wildcard_handlers,
            details={"at": datetime.now(timezone.utc).isoformat()},
        )
        emit(
            "heartbeat.pulse",
            "heart",
            payload={
                "beat_id": beat_id,
                "stream": dna.stream_name,
                "interval_sec": dna.heartbeat_interval,
            },
        )
        return rec


_service: HeartService | None = None


def get_heart_service() -> HeartService:
    global _service
    if _service is not None:
        return _service

    dna = get_heart_dna()
    port: EventBusPort | None = None
    bus = get_bus()
    if not hasattr(bus, "history"):
        try:
            from .adapters.redis_adapter import RedisStreamEventBusAdapter

            port = RedisStreamEventBusAdapter(
                redis_url=dna.redis_url,
                stream_name=dna.stream_name,
            )
            port._client().ping()  # type: ignore[attr-defined]
        except Exception:
            logger.info("Redis replay unavailable; global bus has no in-memory history")

    _service = HeartService(port=port)
    return _service
