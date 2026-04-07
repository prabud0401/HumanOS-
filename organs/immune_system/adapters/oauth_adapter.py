"""
OAuth2 adapter — exchanges authorization codes for tokens (stub + hooks).
"""

from __future__ import annotations

import logging
import os
import urllib.parse

from ..ports import AuthContext, AuthPort, AuthResult, AuthzRequest

logger = logging.getLogger("humanos.immune.adapters.oauth")


class OAuth2AuthAdapter(AuthPort):
    """Authenticate via OAuth2 provider; authorize using local policy table."""

    def __init__(self, token_url: str | None = None, client_id: str | None = None):
        self._token_url = token_url or os.environ.get("OAUTH_TOKEN_URL", "")
        self._client_id = client_id or os.environ.get("OAUTH_CLIENT_ID", "")

    def authenticate(self, ctx: AuthContext) -> AuthResult:
        code = ctx.credentials.get("code")
        if not code or not self._token_url:
            return AuthResult(authenticated=False, details={"reason": "missing_oauth_config_or_code"})
        try:
            # Production: POST with client_secret, redirect_uri, etc.
            logger.info("OAuth token exchange (stub validated presence of code)")
            sub = ctx.credentials.get("subject", "oauth-user")
            return AuthResult(
                authenticated=True,
                subject=sub,
                roles=list(ctx.credentials.get("roles", [])),
                details={"provider": "oauth2"},
            )
        except Exception as exc:
            logger.exception("OAuth authenticate failed")
            return AuthResult(authenticated=False, details={"error": str(exc)})

    def authorize(self, req: AuthzRequest) -> bool:
        from ..models import AccessPolicy
        import fnmatch

        qs = AccessPolicy.objects.filter(is_active=True).order_by("priority")
        for pol in qs:
            if fnmatch.fnmatch(req.resource, pol.resource_pattern):
                if req.action in (pol.actions or []) and (not pol.roles or req.subject in pol.roles):
                    return True
        return False

    def revoke(self, subject: str, reason: str = "") -> None:
        logger.info("OAuth revoke subject=%s reason=%s", subject, reason)


class OAuth2Client:
    """Thin HTTP helper for authorization-code flow (optional use from API layer)."""

    @staticmethod
    def build_authorize_url(authorize_url: str, client_id: str, redirect_uri: str, scope: str, state: str) -> str:
        q = urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
            }
        )
        return f"{authorize_url}?{q}"
