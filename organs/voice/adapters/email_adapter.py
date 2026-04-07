"""
Email — SMTP or Microsoft Graph sendMail (stubbed).
"""

from __future__ import annotations

import logging
from typing import Any

from ..ports import OutboundMessage, SendResult

logger = logging.getLogger("humanos.voice.adapters.email")


def validate_config(config: dict[str, Any]) -> bool:
    return bool(config.get("from_addr")) and bool(config.get("smtp_host") or config.get("graph"))


def connect(config: dict[str, Any]) -> dict[str, Any]:
    return {"reachable": validate_config(config), "transport": "smtp" if config.get("smtp_host") else "graph"}


def send_message(config: dict[str, Any], message: OutboundMessage) -> SendResult:
    if not message.recipient:
        return SendResult(ok=False, error="Email recipient required")
    if not validate_config(config):
        return SendResult(ok=False, error="Email config incomplete")
    logger.info("Email send stub to=%s", message.recipient)
    return SendResult(ok=True, provider_message_id="email-stub")
