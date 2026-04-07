"""
Synchronous transport — routes packets immediately on the calling thread (dev / tests).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

from core.bus import emit

from ..ports import TransitEnvelope, TransportPort

logger = logging.getLogger("humanos.circulatory.sync_transport")


class SyncTransportAdapter(TransportPort):
    """Immediate in-process delivery with optional transform chain."""

    def route(self, envelope: TransitEnvelope) -> str:
        delivery_id = f"sync-{uuid.uuid4().hex[:16]}"
        token = self._receipt_token(envelope)
        logger.info(
            "Sync route %s -> %s (%s)",
            envelope.source_organ,
            envelope.target_organ,
            delivery_id,
        )
        emit(
            "data.delivered",
            "circulatory_system",
            payload={
                "delivery_id": delivery_id,
                "packet_id": envelope.packet_id,
                "target": envelope.target_organ,
                "receipt_token": token,
            },
        )
        return delivery_id

    def transform_in_transit(
        self, payload: dict[str, Any], transforms: list[dict[str, Any]]
    ) -> dict[str, Any]:
        out = dict(payload)
        for step in transforms:
            op = step.get("op")
            if op == "pick_keys" and "keys" in step:
                keys = set(step["keys"])
                out = {k: v for k, v in out.items() if k in keys}
            elif op == "merge" and "data" in step:
                out = {**out, **step["data"]}
            elif op == "redact" and "keys" in step:
                for k in step["keys"]:
                    out.pop(k, None)
        return out

    def validate_delivery(self, envelope: TransitEnvelope, receipt_token: str) -> bool:
        return receipt_token == self._receipt_token(envelope)

    def _receipt_token(self, envelope: TransitEnvelope) -> str:
        raw = json.dumps(
            {
                "packet_id": envelope.packet_id,
                "source": envelope.source_organ,
                "target": envelope.target_organ,
                "payload": envelope.payload,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
