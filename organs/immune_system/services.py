"""
Immune System Service — Wires auth, encryption, threat ports and audit logging.
"""

from __future__ import annotations

import logging
import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone as dj_tz

from core.bus import emit

from .dna import get_immune_system_dna
from .models import AuditLog, EncryptionKey, SecurityEvent
from .ports import (
    AuthContext,
    AuthPort,
    AuthResult,
    AuthzRequest,
    CryptoBlob,
    EncryptionPort,
    ThreatPort,
    ThreatReport,
    ThreatSignal,
)

logger = logging.getLogger("humanos.immune.services")


class FernetEncryptionPort(EncryptionPort):
    """Symmetric encryption using Fernet (cryptography package)."""

    def __init__(self, algorithm: str = "fernet"):
        self._algorithm = algorithm
        self._fernet = None
        try:
            from cryptography.fernet import Fernet
            import base64
            import hashlib
            import os

            key = os.environ.get("IMMUNE_FERNET_KEY", "")
            if not key:
                key = base64.urlsafe_b64encode(hashlib.sha256(b"humanos-dev-key").digest())
            self._fernet = Fernet(key if isinstance(key, bytes) else key.encode())
        except Exception as exc:
            logger.debug("Fernet not available: %s", exc)

    def encrypt(self, plaintext: bytes, key_id: str | None = None) -> CryptoBlob:
        if not self._fernet:
            raise RuntimeError("Encryption not configured")
        ct = self._fernet.encrypt(plaintext)
        kid = key_id or "fernet-default"
        return CryptoBlob(ciphertext=ct, key_id=kid)

    def decrypt(self, blob: CryptoBlob) -> bytes:
        if not self._fernet:
            raise RuntimeError("Encryption not configured")
        return self._fernet.decrypt(blob.ciphertext)

    def rotate_key(self, new_algorithm: str | None = None) -> str:
        new_id = f"key-{uuid.uuid4().hex[:12]}"
        EncryptionKey.objects.create(
            key_id=new_id,
            algorithm=new_algorithm or self._algorithm,
            version=1,
        )
        emit("key.rotated", "immune_system", payload={"key_id": new_id})
        return new_id


class HeuristicThreatPort(ThreatPort):
    def __init__(self, threshold: float):
        self._threshold = threshold

    def detect(self, signal: ThreatSignal) -> ThreatReport:
        score = float(signal.score)
        detected = score >= self._threshold
        sev = "critical" if score >= 0.95 else "high" if score >= 0.85 else "medium"
        return ThreatReport(
            detected=detected,
            severity=sev if detected else "low",
            recommended_action="quarantine" if detected else "monitor",
            metadata={"kind": signal.kind, "source": signal.source, "score": score},
        )

    def quarantine(self, reference: str, reason: str) -> bool:
        logger.warning("Quarantine reference=%s reason=%s", reference, reason)
        return True


class ImmuneSystemService:
    def __init__(
        self,
        auth: AuthPort,
        encryption: EncryptionPort,
        threat: ThreatPort,
    ):
        self._auth = auth
        self._encryption = encryption
        self._threat = threat

    def login(self, principal: str, credentials: dict) -> AuthResult:
        return self._auth.authenticate(AuthContext(principal=principal, credentials=credentials))

    def can(self, subject: str, action: str, resource: str, context: dict | None = None) -> bool:
        allowed = self._auth.authorize(AuthzRequest(subject=subject, action=action, resource=resource, context=context or {}))
        self._audit(subject, action, resource, allowed, "policy_eval")
        if not allowed:
            emit(
                "access.denied",
                "immune_system",
                payload={"subject": subject, "action": action, "resource": resource},
            )
        return allowed

    def _audit(self, actor: str, action: str, resource: str, allowed: bool, reason: str) -> None:
        dna = get_immune_system_dna()
        cutoff = dj_tz.now() - timedelta(days=dna.audit_retention_days)
        AuditLog.objects.filter(created_at__lt=cutoff).delete()
        AuditLog.objects.create(
            log_id=f"audit-{uuid.uuid4().hex[:12]}",
            actor=actor,
            action=action,
            resource=resource,
            allowed=allowed,
            reason=reason,
        )

    def seal(self, data: bytes) -> CryptoBlob:
        dna = get_immune_system_dna()
        return self._encryption.encrypt(data, key_id=None)

    def reveal(self, blob: CryptoBlob) -> bytes:
        return self._encryption.decrypt(blob)

    def evaluate_threat(self, signal: ThreatSignal) -> ThreatReport:
        report = self._threat.detect(signal)
        if report.detected:
            emit(
                "threat.detected",
                "immune_system",
                payload=report.metadata | {"severity": report.severity},
            )
            with transaction.atomic():
                SecurityEvent.objects.create(
                    event_id=f"sec-{uuid.uuid4().hex[:12]}",
                    title=f"Threat: {signal.kind}",
                    description=signal.kind,
                    severity=SecurityEvent.Severity.HIGH,
                    status=SecurityEvent.Status.OPEN,
                    context=signal.evidence,
                )
        return report


_service: ImmuneSystemService | None = None


def get_immune_system_service() -> ImmuneSystemService:
    global _service
    if _service is None:
        dna = get_immune_system_dna()
        from .adapters.jwt_adapter import JWTAuthAdapter

        _service = ImmuneSystemService(
            auth=JWTAuthAdapter(algorithm="HS256"),
            encryption=FernetEncryptionPort(algorithm=dna.encryption_algorithm),
            threat=HeuristicThreatPort(dna.threat_threshold),
        )
    return _service
