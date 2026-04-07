"""
Google Meet / Calendar — related Drive files and Meet artifacts (via Calendar + Drive API).
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..ports import ArtifactRef, AuthContext, MeetingIngestionPort, MeetingRef

logger = logging.getLogger("humanos.lungs.adapters.google_meet")


class GoogleMeetIngestionAdapter(MeetingIngestionPort):
    """Uses Google Calendar event attachments and Meet recording links when available."""

    def authenticate(self) -> AuthContext:
        logger.debug("Google Meet adapter authenticate (stub)")
        return AuthContext(provider="google_meet", access_token="", extra={})

    def discover_artifacts(self, meeting: MeetingRef, auth: AuthContext) -> list[ArtifactRef]:
        if not auth.access_token:
            return []
        return [
            ArtifactRef(
                external_id=f"gcal:{meeting.meeting_id}:notes",
                name="meet_notes.txt",
                mime_type="text/plain",
                metadata=meeting.metadata,
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
        logger.info("Google Meet placeholder write %s", target)
        return target
