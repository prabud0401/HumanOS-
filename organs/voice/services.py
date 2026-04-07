"""
Voice Service Layer — routes notifications through channel adapters with cooldowns.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.core.cache import cache
from django.utils import timezone

from core.bus import Event, emit

from .dna import get_voice_dna
from .models import Channel, Notification, NotificationTemplate
from .ports import NotificationPort, OutboundMessage, SendResult

logger = logging.getLogger("humanos.voice.services")


def _dispatch_send(channel: Channel, message: OutboundMessage) -> SendResult:
    cfg = channel.config or {}
    if channel.kind == Channel.Kind.SLACK:
        from .adapters import slack_adapter

        return slack_adapter.send_message(cfg, message)
    if channel.kind == Channel.Kind.EMAIL:
        from .adapters import email_adapter

        return email_adapter.send_message(cfg, message)
    if channel.kind == Channel.Kind.TEAMS_CHAT:
        from .adapters import teams_chat_adapter

        return teams_chat_adapter.send_message(cfg, message)
    return SendResult(ok=False, error=f"Unknown channel kind: {channel.kind}")


class VoiceService(NotificationPort):
    def resolve_channel_slug(self, event_type: str) -> str:
        dna = get_voice_dna()
        for rule in dna.escalation_rules:
            if rule.get("event_type") == event_type and rule.get("channel"):
                return str(rule["channel"])
        return dna.default_channel

    def _cooldown_allows(self, channel_slug: str, event_type: str) -> bool:
        dna = get_voice_dna()
        key = f"voice:cooldown:{channel_slug}:{event_type}"
        if cache.get(key):
            return False
        cache.set(key, 1, timeout=max(1, dna.notification_cooldown))
        return True

    def send(self, channel_slug: str, message: OutboundMessage) -> SendResult:
        try:
            ch = Channel.objects.get(slug=channel_slug, is_active=True)
        except Channel.DoesNotExist:
            return SendResult(ok=False, error=f"Channel not found: {channel_slug}")
        return _dispatch_send(ch, message)

    def send_batch(self, channel_slug: str, messages: list[OutboundMessage]) -> list[SendResult]:
        return [self.send(channel_slug, m) for m in messages]

    def notify_from_event(self, event: Event) -> Notification | None:
        slug = self.resolve_channel_slug(event.type)
        if not self._cooldown_allows(slug, event.type):
            logger.debug("Voice cooldown active for %s / %s", slug, event.type)
            return None

        try:
            ch = Channel.objects.get(slug=slug, is_active=True)
        except Channel.DoesNotExist:
            emit(
                "notification.failed",
                "voice",
                payload={"reason": "no_channel", "slug": slug, "event_type": event.type},
            )
            return None

        tmpl = NotificationTemplate.objects.filter(channel=ch, is_active=True).first()
        subject, body = self._render(tmpl, event.payload or {})

        nid = f"ntf-{uuid.uuid4().hex[:12]}"
        note = Notification.objects.create(
            notification_id=nid,
            channel=ch,
            template=tmpl,
            event_type=event.type,
            payload=event.payload or {},
            rendered_subject=subject,
            rendered_body=body,
            status=Notification.Status.QUEUED,
        )

        result = _dispatch_send(
            ch,
            OutboundMessage(
                subject=subject,
                body=body,
                recipient=(event.payload or {}).get("recipient", ""),
                metadata={"notification_id": nid},
            ),
        )

        if result.ok:
            note.status = Notification.Status.SENT
            note.sent_at = timezone.now()
            note.save(update_fields=["status", "sent_at"])
            emit(
                "notification.sent",
                "voice",
                payload={"notification_id": nid, "channel": slug, "source_event": event.event_id},
            )
        else:
            note.status = Notification.Status.FAILED
            note.error_message = result.error
            note.save(update_fields=["status", "error_message"])
            emit(
                "notification.failed",
                "voice",
                payload={"notification_id": nid, "error": result.error},
            )
        return note

    def _render(self, tmpl: NotificationTemplate | None, payload: dict[str, Any]) -> tuple[str, str]:
        if tmpl:
            try:
                subj = tmpl.subject.format(**payload) if tmpl.subject else ""
            except Exception:
                subj = tmpl.subject
            try:
                body = tmpl.body.format(**payload) if tmpl.body else ""
            except Exception:
                body = tmpl.body
            return subj, body
        title = str(payload.get("title") or payload.get("action") or "HumanOS notification")
        return title, f"{title}\n\n{payload!r}"


_service: VoiceService | None = None


def get_voice_service() -> VoiceService:
    global _service
    if _service is None:
        _service = VoiceService()
    return _service
