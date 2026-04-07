"""
Lungs Events — ingestion lifecycle on the bus.
"""

import logging
import uuid

from core.bus import Event, emit

logger = logging.getLogger("humanos.lungs.events")

PUBLISHES = [
    "artifacts.ingested",
    "ingestion.failed",
]

SUBSCRIBES = [
    "meeting.detected",
    "meeting.retry",
]


def handle_event(event: Event) -> None:
    if event.type == "meeting.detected":
        _on_meeting_detected(event)
    elif event.type == "meeting.retry":
        _on_meeting_retry(event)
    else:
        logger.warning("Lungs received unexpected event: %s", event.type)


def _on_meeting_detected(event: Event) -> None:
    from .services import get_lungs_service

    payload = event.payload or {}
    provider = payload.get("provider", "teams")
    meeting_id = payload.get("meeting_id", "")
    title = payload.get("title", "")
    job_id = payload.get("job_id") or f"ing-{uuid.uuid4().hex[:12]}"
    logger.info("Lungs scheduling ingestion job=%s meeting=%s", job_id, meeting_id)
    try:
        get_lungs_service().ingest_meeting(
            job_id=job_id,
            provider=provider,
            meeting_id=meeting_id,
            title=title,
            metadata=payload,
        )
    except Exception as exc:
        logger.exception("Ingestion failed for %s", job_id)
        emit(
            "ingestion.failed",
            "lungs",
            payload={"job_id": job_id, "error": str(exc), "phase": "meeting.detected"},
        )


def _on_meeting_retry(event: Event) -> None:
    from .services import get_lungs_service

    payload = event.payload or {}
    job_id = payload.get("job_id", "")
    if not job_id:
        logger.error("meeting.retry missing job_id")
        return
    logger.info("Lungs retry requested for job=%s", job_id)
    try:
        get_lungs_service().retry_job(job_id)
    except Exception as exc:
        emit(
            "ingestion.failed",
            "lungs",
            payload={"job_id": job_id, "error": str(exc), "phase": "retry"},
        )
