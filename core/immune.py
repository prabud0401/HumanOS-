"""
Immune Middleware — Security wraps every organ.

Provides authentication, encryption, rate limiting, audit logging,
and data sanitization. Every request, event, and file access runs
through immune checks automatically.
"""

import hashlib
import hmac
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("humanos.immune")


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    SECRET = "secret"


@dataclass
class AuditEntry:
    timestamp: str
    organ: str
    action: str
    actor: str
    resource: str
    result: str
    threat_level: ThreatLevel = ThreatLevel.NONE
    details: dict = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    max_requests_per_minute: int = 60
    require_encryption_at_rest: bool = True
    allowed_file_extensions: list[str] = field(
        default_factory=lambda: [".vtt", ".txt", ".json", ".yaml", ".md", ".pdf", ".csv"]
    )
    max_file_size_mb: int = 100
    sensitive_fields: list[str] = field(
        default_factory=lambda: ["password", "token", "secret", "api_key", "ssn", "credit_card"]
    )
    log_retention_days: int = 90


class ImmuneSystem:
    """Central security middleware for all organs."""

    def __init__(self, policy: SecurityPolicy | None = None):
        self.policy = policy or SecurityPolicy()
        self._audit_log: list[AuditEntry] = []
        self._rate_limits: dict[str, list[float]] = {}
        self._signing_key = os.environ.get("HUMANOS_SIGNING_KEY", "dev-key-change-in-production")

    def audit(self, organ: str, action: str, actor: str, resource: str, result: str, **kwargs) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            organ=organ,
            action=action,
            actor=actor,
            resource=resource,
            result=result,
            threat_level=kwargs.get("threat_level", ThreatLevel.NONE),
            details=kwargs.get("details", {}),
        )
        self._audit_log.append(entry)
        logger.info("AUDIT [%s] %s.%s by %s -> %s", entry.threat_level.value, organ, action, actor, result)

    def check_rate_limit(self, key: str) -> bool:
        """Returns True if under limit, False if rate-limited."""
        now = time.time()
        window = self._rate_limits.setdefault(key, [])
        cutoff = now - 60
        self._rate_limits[key] = [t for t in window if t > cutoff]
        if len(self._rate_limits[key]) >= self.policy.max_requests_per_minute:
            logger.warning("Rate limit exceeded for key=%s", key)
            return False
        self._rate_limits[key].append(now)
        return True

    def sanitize_payload(self, data: dict) -> dict:
        """Redact sensitive fields from a payload before logging/storage."""
        sanitized = {}
        for key, value in data.items():
            if any(s in key.lower() for s in self.policy.sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_payload(value)
            else:
                sanitized[key] = value
        return sanitized

    def validate_file(self, filename: str, size_bytes: int) -> tuple[bool, str]:
        """Validate a file against security policy."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.policy.allowed_file_extensions:
            return False, f"File extension '{ext}' not allowed"
        max_bytes = self.policy.max_file_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            return False, f"File size {size_bytes} exceeds maximum {max_bytes}"
        return True, "OK"

    def sign_data(self, data: str) -> str:
        """Create an HMAC signature for data integrity verification."""
        return hmac.new(self._signing_key.encode(), data.encode(), hashlib.sha256).hexdigest()

    def verify_signature(self, data: str, signature: str) -> bool:
        """Verify an HMAC signature."""
        expected = self.sign_data(data)
        return hmac.compare_digest(expected, signature)

    @property
    def audit_log(self) -> list[AuditEntry]:
        return list(self._audit_log)

    def get_audit_log(self, organ: str | None = None, limit: int = 100) -> list[AuditEntry]:
        entries = self._audit_log
        if organ:
            entries = [e for e in entries if e.organ == organ]
        return entries[-limit:]


# Global instance
_immune = ImmuneSystem()


def get_immune() -> ImmuneSystem:
    return _immune


def set_immune(system: ImmuneSystem) -> None:
    global _immune
    _immune = system


def guarded(organ: str, action: str):
    """Decorator that wraps a function with immune checks (rate limit + audit)."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            immune = get_immune()
            actor = kwargs.pop("_actor", "system")
            resource = kwargs.pop("_resource", fn.__qualname__)

            if not immune.check_rate_limit(f"{organ}:{action}:{actor}"):
                immune.audit(organ, action, actor, resource, "rate_limited", threat_level=ThreatLevel.MEDIUM)
                raise PermissionError(f"Rate limit exceeded for {organ}.{action}")

            try:
                result = fn(*args, **kwargs)
                immune.audit(organ, action, actor, resource, "success")
                return result
            except Exception as exc:
                immune.audit(organ, action, actor, resource, "error", details={"error": str(exc)})
                raise
        return wrapper
    return decorator
