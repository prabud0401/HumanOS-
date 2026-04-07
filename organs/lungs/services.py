"""
Lungs Service Layer — provider adapters, job state, artifact persistence.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from django.utils import timezone

from core.bus import emit

from .dna import get_lungs_dna
from .models import Artifact, IngestionJob
from .ports import ArtifactRef, MeetingIngestionPort, MeetingRef

logger = logging.getLogger("humanos.lungs.services")


def _adapter_for_provider(name: str) -> MeetingIngestionPort:
    n = (name or "teams").lower()
    if n == "zoom":
        from .adapters.zoom_adapter import ZoomMeetingIngestionAdapter

        return ZoomMeetingIngestionAdapter()
    if n in ("google_meet", "google-meet", "meet"):
        from .adapters.google_meet_adapter import GoogleMeetIngestionAdapter

        return GoogleMeetIngestionAdapter()
    from .adapters.teams_adapter import TeamsMeetingIngestionAdapter

    return TeamsMeetingIngestionAdapter()


class LungsService:
    def __init__(self):
        self._dna = get_lungs_dna()

    def ingest_meeting(
        self,
        *,
        job_id: str,
        provider: str,
        meeting_id: str,
        title: str = "",
        metadata: dict | None = None,
    ) -> IngestionJob:
        if not job_id:
            job_id = f"ing-{uuid.uuid4().hex[:12]}"
        dna = self._dna
        dna.download_path.mkdir(parents=True, exist_ok=True)

        job, _ = IngestionJob.objects.get_or_create(
            job_id=job_id,
            defaults={
                "source": _source_choice(provider),
                "external_ref": meeting_id,
                "status": IngestionJob.Status.PENDING,
                "metadata": metadata or {},
            },
        )
        job.status = IngestionJob.Status.RUNNING
        job.save(update_fields=["status", "updated_at"])

        adapter = _adapter_for_provider(provider)
        meeting = MeetingRef(provider=provider, meeting_id=meeting_id, title=title, metadata=metadata or {})

        try:
            auth = adapter.authenticate()
            refs = adapter.discover_artifacts(meeting, auth)
            dest = dna.download_path / job_id
            artifact_rows: list[Artifact] = []
            for ref in refs[: dna.max_concurrent_downloads]:
                path = adapter.download(meeting, ref, auth, dest)
                artifact_rows.append(
                    Artifact.objects.create(
                        artifact_id=f"art-{uuid.uuid4().hex[:12]}",
                        job=job,
                        kind=_guess_kind(ref),
                        logical_name=ref.name,
                        storage_path=str(path.resolve()),
                        content_type=ref.mime_type,
                        byte_size=path.stat().st_size if path.exists() else 0,
                        metadata=ref.metadata,
                    )
                )

            job.status = IngestionJob.Status.COMPLETED
            job.completed_at = timezone.now()
            job.error_message = ""
            job.save(update_fields=["status", "completed_at", "error_message", "updated_at"])

            emit(
                "artifacts.ingested",
                "lungs",
                payload={
                    "job_id": job_id,
                    "artifact_ids": [a.artifact_id for a in artifact_rows],
                    "count": len(artifact_rows),
                },
            )
        except Exception as exc:
            job.status = IngestionJob.Status.FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message", "updated_at"])
            emit(
                "ingestion.failed",
                "lungs",
                payload={"job_id": job_id, "error": str(exc)},
            )
            raise

        return job

    def retry_job(self, job_id: str) -> IngestionJob:
        job = IngestionJob.objects.get(job_id=job_id)
        dna = self._dna
        if job.retry_count >= dna.retry_count:
            raise RuntimeError(f"Max retries ({dna.retry_count}) exceeded for {job_id}")
        job.retry_count += 1
        job.status = IngestionJob.Status.PENDING
        job.error_message = ""
        job.save(update_fields=["retry_count", "status", "error_message", "updated_at"])
        return self.ingest_meeting(
            job_id=job.job_id,
            provider=job.source,
            meeting_id=job.external_ref,
            title=job.metadata.get("title", ""),
            metadata=job.metadata,
        )


def _source_choice(provider: str) -> str:
    p = provider.lower()
    mapping = {
        "teams": IngestionJob.Source.TEAMS,
        "zoom": IngestionJob.Source.ZOOM,
        "google_meet": IngestionJob.Source.GOOGLE_MEET,
        "meet": IngestionJob.Source.GOOGLE_MEET,
    }
    return mapping.get(p, IngestionJob.Source.OTHER)


def _guess_kind(ref: ArtifactRef) -> str:
    mt = (ref.mime_type or "").lower()
    if "video" in mt:
        return Artifact.Kind.RECORDING
    if "text/vtt" in mt or "transcript" in ref.name.lower():
        return Artifact.Kind.TRANSCRIPT
    return Artifact.Kind.FILE


_service: LungsService | None = None


def get_lungs_service() -> LungsService:
    global _service
    if _service is None:
        _service = LungsService()
    return _service
