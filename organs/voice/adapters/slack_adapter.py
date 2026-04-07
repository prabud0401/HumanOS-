"""
Slack — incoming webhooks or chat.postMessage (stubbed).
"""

from __future__ import annotations

import logging
from typing import Any

from ..ports import OutboundMessage, SendResult

logger = logging.getLogger("humanos.voice.adapters.slack")


def validate_config(config: dict[str, Any]) -> bool:
    return bool(config.get("webhook_url") or config.get("bot_token"))


def connect(config: dict[str, Any]) -> dict[str, Any]:
    ok = validate_config(config)
    return {"reachable": ok, "mode": "webhook" if config.get("webhook_url") else "bot"}


def send_message(config: dict[str, Any], message: OutboundMessage) -> SendResult:
    if not validate_config(config):
        return SendResult(ok=False, error="Slack config missing webhook_url or bot_token")
    logger.info("Slack send stub subject=%s", message.subject[:50] if message.subject else "")
    # Production: requests.post(webhook_url, json={...}) or WebClient.chat_postMessage
    return SendResult(ok=True, provider_message_id="slack-stub")
