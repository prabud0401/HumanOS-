"""
Zoom API — cloud recordings and meeting artifacts.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..ports import ArtifactRef, AuthContext, MeetingIngestionPort, MeetingRef

logger = logging.getLogger("humanos.lungs.adapters.zoom")


class ZoomMeetingIngestionAdapter(MeetingIngestionPort):
    """Server-to-server OAuth and recordings endpoints — configure credentials for production."""

    def authenticate(self) -> AuthContext:
        logger.debug("Zoom adapter authenticate (stub)")
        return AuthContext(provider="zoom", access_token="", extra={})

    def discover_artifacts(self, meeting: MeetingRef, auth: AuthContext) -> list[ArtifactRef]:
        if not auth.access_token:
            return []
        return [
            ArtifactRef(
                external_id=f"zoom:{meeting.meeting_id}:m4a",
                name="audio_only.m4a",
                mime_type="audio/mp4",
                metadata={"uuid": meeting.meeting_id},
            ),
        ]

    def download(
        self,
        meeting: MeetingRef,
        artifact: ArtifactRef,
        auth: AuthContext,
        dest_dir: Path,
    ) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)
        target = dest_dir / artifact.name.replace("/", "_")
        target.write_bytes(b"")
        logger.info("Zoom placeholder write %s", target)
        return target
