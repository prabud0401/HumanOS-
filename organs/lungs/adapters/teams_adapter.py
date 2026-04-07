"""
Microsoft Teams / Graph — meeting recordings and transcripts.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..ports import ArtifactRef, AuthContext, MeetingIngestionPort, MeetingRef

logger = logging.getLogger("humanos.lungs.adapters.teams")


class TeamsMeetingIngestionAdapter(MeetingIngestionPort):
    """Uses Microsoft Graph (onlineMeetings, drive items, callRecords) — wire tokens in production."""

    def authenticate(self) -> AuthContext:
        # Production: MSAL confidential client or delegated flow
        logger.debug("Teams adapter authenticate (stub — configure Graph credentials)")
        return AuthContext(provider="teams", access_token="", extra={})

    def discover_artifacts(self, meeting: MeetingRef, auth: AuthContext) -> list[ArtifactRef]:
        if not auth.access_token:
            logger.warning("Teams discovery skipped — no access token")
            return []
        return [
            ArtifactRef(
                external_id=f"{meeting.meeting_id}:recording",
                name=f"{meeting.title or 'meeting'}.mp4",
                mime_type="video/mp4",
                metadata={"graph_meeting_id": meeting.meeting_id},
            ),
            ArtifactRef(
                external_id=f"{meeting.meeting_id}:transcript",
                name="transcript.vtt",
                mime_type="text/vtt",
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
        # Production: GET contentUrl from Graph, stream to disk
        target.write_bytes(b"")
        logger.info("Teams placeholder write %s", target)
        return target
