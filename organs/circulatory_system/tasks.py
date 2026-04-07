"""
Circulatory Celery tasks — async packet delivery.
"""

import logging

logger = logging.getLogger("humanos.circulatory.tasks")

try:
    from celery import shared_task

    @shared_task(name="circulatory_system.apply_pipeline_delivery")
    def apply_pipeline_delivery(
        packet_id: str,
        source_organ: str,
        target_organ: str,
        payload: dict,
        metadata: dict,
        delivery_id: str,
    ) -> dict:
        """Worker: perform delivery and emit bus confirmation."""
        from .adapters.sync_transport import SyncTransportAdapter
        from .ports import TransitEnvelope

        envelope = TransitEnvelope(
            packet_id=packet_id,
            source_organ=source_organ,
            target_organ=target_organ,
            payload=payload,
            metadata={**metadata, "async_delivery_id": delivery_id},
        )
        # SyncTransportAdapter.route emits data.delivered with its own delivery id
        SyncTransportAdapter().route(envelope)
        return {"delivery_id": delivery_id, "packet_id": packet_id}

except ImportError:
    logger.debug("Celery not installed — circulatory tasks are stubs")

    def apply_pipeline_delivery(packet_id, source_organ, target_organ, payload, metadata, delivery_id):
        raise RuntimeError("Celery required for async circulatory transport")
