"""
JWT adapter — issue and validate JSON Web Tokens for service-to-service auth.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

from ..ports import AuthContext, AuthPort, AuthResult, AuthzRequest

logger = logging.getLogger("humanos.immune.adapters.jwt")


class JWTAuthAdapter(AuthPort):
    """Authenticate via JWT (PyJWT); authorize reuses AccessPolicy like OAuth adapter."""

    def __init__(self, secret: str | None = None, algorithm: str = "HS256"):
        self._secret = secret or os.environ.get("JWT_SECRET", "change-me-in-production")
        self._algorithm = algorithm

    def authenticate(self, ctx: AuthContext) -> AuthResult:
        token = ctx.credentials.get("token") or ctx.credentials.get("jwt")
        if not token:
            return AuthResult(authenticated=False, details={"reason": "missing_token"})
        try:
            import jwt

            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            sub = str(payload.get("sub", ""))
            roles = list(payload.get("roles", []))
            return AuthResult(
                authenticated=True,
                subject=sub,
                roles=roles,
                expires_at=str(payload.get("exp", "")),
                details={"issuer": payload.get("iss")},
            )
        except ImportError:
            logger.error("PyJWT not installed")
            return AuthResult(authenticated=False, details={"reason": "pyjwt_missing"})
        except Exception as exc:
            return AuthResult(authenticated=False, details={"error": str(exc)})

    def authorize(self, req: AuthzRequest) -> bool:
        from fnmatch import fnmatch

        from ..models import AccessPolicy

        for pol in AccessPolicy.objects.filter(is_active=True).order_by("priority"):
            if fnmatch(req.resource, pol.resource_pattern):
                if req.action in (pol.actions or []) and (not pol.roles or req.subject in pol.roles):
                    return True
        return False

    def revoke(self, subject: str, reason: str = "") -> None:
        logger.info("JWT revoke (stateless) subject=%s — add denylist in production", subject)

    def issue_token(
        self,
        subject: str,
        roles: list[str],
        ttl_seconds: int,
        extra_claims: dict | None = None,
    ) -> str:
        import jwt

        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "roles": roles,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
