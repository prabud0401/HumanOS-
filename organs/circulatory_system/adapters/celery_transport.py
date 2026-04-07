"""
Celery-backed async transport — enqueues delivery tasks for worker pools.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from ..ports import TransitEnvelope, TransportPort

logger = logging.getLogger("humanos.circulatory.celery_transport")


class CeleryTransportAdapter(TransportPort):
    """Delegates routing to Celery tasks when available."""

    def __init__(self) -> None:
        self._apply_task = None
        try:
            from ..tasks import apply_pipeline_delivery

            self._apply_task = apply_pipeline_delivery
        except (ImportError, RuntimeError):
            logger.debug("Celery task apply_pipeline_delivery not available")

    def route(self, envelope: TransitEnvelope) -> str:
        delivery_id = f"celery-{uuid.uuid4().hex[:16]}"
        if self._apply_task is not None:
            self._apply_task.delay(
                packet_id=envelope.packet_id,
                source_organ=envelope.source_organ,
                target_organ=envelope.target_organ,
                payload=envelope.payload,
                metadata=envelope.metadata,
                delivery_id=delivery_id,
            )
            logger.info("Enqueued delivery %s", delivery_id)
        else:
            logger.warning("Celery unavailable — falling back to no-op enqueue for %s", delivery_id)
        return delivery_id

    def transform_in_transit(
        self, payload: dict[str, Any], transforms: list[dict[str, Any]]
    ) -> dict[str, Any]:
        from .sync_transport import SyncTransportAdapter

        return SyncTransportAdapter().transform_in_transit(payload, transforms)

    def validate_delivery(self, envelope: TransitEnvelope, receipt_token: str) -> bool:
        from .sync_transport import SyncTransportAdapter

        return SyncTransportAdapter().validate_delivery(envelope, receipt_token)
