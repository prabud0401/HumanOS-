"""
Lungs Ports — Meeting and artifact ingestion contracts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuthContext:
    """Opaque credentials bundle for a provider (tokens, tenant ids)."""

    provider: str
    access_token: str = ""
    refresh_token: str = ""
    expires_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MeetingRef:
    """Minimal handle to a meeting in an external system."""

    provider: str
    meeting_id: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactRef:
    """Remote artifact descriptor before download."""

    external_id: str
    name: str
    mime_type: str = ""
    size_bytes: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class MeetingIngestionPort(ABC):
    """Authenticate, enumerate artifacts, and download for one meeting stack."""

    @abstractmethod
    def authenticate(self) -> AuthContext:
        """Obtain or refresh credentials for this provider."""

    @abstractmethod
    def discover_artifacts(self, meeting: MeetingRef, auth: AuthContext) -> list[ArtifactRef]:
        """List artifacts available for the given meeting."""

    @abstractmethod
    def download(
        self,
        meeting: MeetingRef,
        artifact: ArtifactRef,
        auth: AuthContext,
        dest_dir: Path,
    ) -> Path:
        """Download a single artifact to dest_dir; return final file path."""
