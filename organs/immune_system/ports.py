"""
Immune System Ports — Authentication, encryption, and threat handling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthContext:
    principal: str
    credentials: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    authenticated: bool
    subject: str = ""
    roles: list[str] = field(default_factory=list)
    expires_at: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthzRequest:
    subject: str
    action: str
    resource: str
    context: dict[str, Any] = field(default_factory=dict)


class AuthPort(ABC):
    @abstractmethod
    def authenticate(self, ctx: AuthContext) -> AuthResult:
        """Validate credentials and return subject + roles."""

    @abstractmethod
    def authorize(self, req: AuthzRequest) -> bool:
        """Return True if subject may perform action on resource."""

    @abstractmethod
    def revoke(self, subject: str, reason: str = "") -> None:
        """Invalidate sessions/tokens for a subject."""


@dataclass
class CryptoBlob:
    ciphertext: bytes
    key_id: str
    nonce: bytes | None = None
    associated_data: bytes | None = None


class EncryptionPort(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes, key_id: str | None = None) -> CryptoBlob:
        """Encrypt plaintext with active or specified key."""

    @abstractmethod
    def decrypt(self, blob: CryptoBlob) -> bytes:
        """Decrypt ciphertext."""

    @abstractmethod
    def rotate_key(self, new_algorithm: str | None = None) -> str:
        """Create a new key version; returns new key_id."""


@dataclass
class ThreatSignal:
    source: str
    kind: str
    score: float
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatReport:
    detected: bool
    severity: str
    recommended_action: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ThreatPort(ABC):
    @abstractmethod
    def detect(self, signal: ThreatSignal) -> ThreatReport:
        """Score a signal and classify threat level."""

    @abstractmethod
    def quarantine(self, reference: str, reason: str) -> bool:
        """Isolate a resource, token, or connection."""
