"""
Microsoft Teams chat — webhook or Graph chatMessage (stubbed).
"""

from __future__ import annotations

import logging
from typing import Any

from ..ports import OutboundMessage, SendResult

logger = logging.getLogger("humanos.voice.adapters.teams_chat")


def validate_config(config: dict[str, Any]) -> bool:
    return bool(config.get("webhook_url") or config.get("team_id"))


def connect(config: dict[str, Any]) -> dict[str, Any]:
    return {"reachable": validate_config(config)}


def send_message(config: dict[str, Any], message: OutboundMessage) -> SendResult:
    if not validate_config(config):
        return SendResult(ok=False, error="Teams chat config incomplete")
    text = message.body or message.subject
    logger.info("Teams chat send stub len=%s", len(text))
    return SendResult(ok=True, provider_message_id="teams-stub")
