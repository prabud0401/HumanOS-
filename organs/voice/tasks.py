"""
Voice Celery Tasks — batched or deferred notifications.
"""

import logging

logger = logging.getLogger("humanos.voice.tasks")

try:
    from celery import shared_task

    @shared_task(name="voice.send_batch")
    def send_batch_task(channel_slug: str, messages: list[dict]) -> dict:
        from .ports import OutboundMessage
        from .services import get_voice_service

        out_messages = [
            OutboundMessage(
                subject=m.get("subject", ""),
                body=m.get("body", ""),
                recipient=m.get("recipient", ""),
                metadata=m.get("metadata") or {},
            )
            for m in messages
        ]
        results = get_voice_service().send_batch(channel_slug, out_messages)
        return {"results": [{"ok": r.ok, "error": r.error} for r in results]}

except ImportError:
    logger.debug("Celery not installed — voice tasks are stubs")

    def send_batch_task(channel_slug, messages):
        raise RuntimeError("Celery required for voice.send_batch")
