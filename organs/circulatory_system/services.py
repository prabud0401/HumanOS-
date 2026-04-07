"""
Circulatory service layer — orchestrates transport port, DNA limits, and models.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.utils import timezone

from core.bus import Event, emit

from .dna import get_circulatory_dna
from .models import DataPacket, Pipeline, PipelineRun
from .ports import TransitEnvelope, TransportPort

logger = logging.getLogger("humanos.circulatory.services")


class CirculatoryService:
    """Pipeline orchestration and transport."""

    def __init__(self, transport: TransportPort) -> None:
        self._transport = transport

    def on_data_ready(self, event: Event) -> None:
        """Prepare a packet when upstream organ signals data.ready."""
        dna = get_circulatory_dna()
        payload = event.payload or {}
        approx_size = len(str(payload).encode("utf-8"))
        if approx_size > dna.max_packet_size:
            emit(
                "transport.failed",
                "circulatory_system",
                payload={
                    "reason": "max_packet_size_exceeded",
                    "approx_size": approx_size,
                    "limit": dna.max_packet_size,
                },
            )
            return
        packet_id = payload.get("packet_id") or f"pkt-{uuid.uuid4().hex}"
        DataPacket.objects.update_or_create(
            packet_id=packet_id,
            defaults={
                "payload_summary": {k: payload.get(k) for k in ("kind", "ref", "organ") if k in payload},
                "byte_size": approx_size,
                "state": DataPacket.State.QUEUED,
            },
        )

    def on_pipeline_trigger(self, event: Event) -> None:
        """Start or continue a pipeline run from a trigger event."""
        slug = (event.payload or {}).get("pipeline_slug")
        if not slug:
            logger.error("pipeline.trigger missing pipeline_slug")
            return
        try:
            pipeline = Pipeline.objects.get(slug=slug, is_active=True)
        except Pipeline.DoesNotExist:
            emit(
                "transport.failed",
                "circulatory_system",
                payload={"reason": "unknown_pipeline", "slug": slug},
            )
            return

        run = PipelineRun.objects.create(
            pipeline=pipeline,
            status=PipelineRun.Status.RUNNING,
            trigger_event_id=event.event_id,
            started_at=timezone.now(),
        )
        try:
            raw_payload = (event.payload or {}).get("payload") or {}
            transformed = self._transport.transform_in_transit(
                raw_payload, pipeline.transform_chain or []
            )
            envelope = TransitEnvelope(
                packet_id=(event.payload or {}).get("packet_id", f"pkt-{uuid.uuid4().hex}"),
                source_organ=pipeline.source_organ,
                target_organ=pipeline.target_organ,
                payload=transformed,
                metadata={"pipeline_run_id": str(run.run_id)},
            )
            delivery_id = self._transport.route(envelope)
            run.status = PipelineRun.Status.COMPLETED
            run.stats = {"delivery_id": delivery_id}
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "stats", "finished_at"])
            emit(
                "pipeline.completed",
                "circulatory_system",
                payload={"run_id": str(run.run_id), "pipeline": slug, "delivery_id": delivery_id},
            )
        except Exception as exc:
            logger.exception("Pipeline run failed")
            run.status = PipelineRun.Status.FAILED
            run.error_message = str(exc)
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "error_message", "finished_at"])
            emit(
                "transport.failed",
                "circulatory_system",
                payload={"run_id": str(run.run_id), "error": str(exc)},
            )

    def deliver_envelope(self, envelope: TransitEnvelope) -> str:
        """Public API for direct envelope routing."""
        return self._transport.route(envelope)


_service: CirculatoryService | None = None


def get_circulatory_service() -> CirculatoryService:
    global _service
    if _service is not None:
        return _service

    dna = get_circulatory_dna()
    if dna.transport_mode == "async":
        from .adapters.celery_transport import CeleryTransportAdapter

        transport: TransportPort = CeleryTransportAdapter()
    else:
        from .adapters.sync_transport import SyncTransportAdapter

        transport = SyncTransportAdapter()

    _service = CirculatoryService(transport=transport)
    return _service
