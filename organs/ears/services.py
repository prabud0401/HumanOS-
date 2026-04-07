"""
Ears Service Layer — polling calendars and recording detections.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from core.bus import emit

from .dna import get_ears_dna
from .models import DetectedEvent, Listener
from .ports import CalendarEventDTO, CalendarPort, WebhookPort

logger = logging.getLogger("humanos.ears.services")


def _calendar_adapter_for_listener(listener: Listener) -> CalendarPort:
    if listener.kind == Listener.Kind.GOOGLE_CALENDAR:
        from .adapters.google_calendar_adapter import GoogleCalendarAdapter

        return GoogleCalendarAdapter()
    from .adapters.outlook_adapter import OutlookCalendarAdapter

    return OutlookCalendarAdapter()


class EarsService:
    def __init__(self):
        self._dna = get_ears_dna()

    def refresh_listener_cache(self, listener: Listener) -> None:
        logger.debug("Listener cache refresh noop for %s", listener.name)

    def poll_calendars(self) -> int:
        """Poll watched calendars from DNA + active DB listeners; emit calendar.event / meeting.detected."""
        dna = self._dna
        count = 0
        calendars = list(dict.fromkeys(dna.watched_calendars))
        for lst in Listener.objects.filter(is_active=True):
            cid = lst.config.get("calendar_id")
            if cid:
                calendars.append(cid)
        calendars = list(dict.fromkeys(calendars))
        if not calendars:
            calendars = ["primary"]

        since = datetime.now(timezone.utc) - timedelta(hours=24)
        for cal_id in calendars:
            listener = (
                Listener.objects.filter(is_active=True, config__calendar_id=cal_id).first()
                or Listener.objects.filter(is_active=True).first()
            )
            adapter = _calendar_adapter_for_listener(listener) if listener else OutlookCalendarAdapter()
            events = adapter.list_events(calendar_id=cal_id, since=since)
            for ev in events:
                self._record_and_emit(cal_id, ev, listener)
                count += 1
        return count

    def _record_and_emit(self, calendar_id: str, ev: CalendarEventDTO, listener: Listener | None) -> None:
        det_id = f"det-{uuid.uuid4().hex[:12]}"
        DetectedEvent.objects.create(
            detection_id=det_id,
            listener=listener,
            signal_type="calendar.event",
            raw_payload={"calendar_id": calendar_id},
            normalized_payload={
                "external_id": ev.external_id,
                "title": ev.title,
                "start": ev.start.isoformat(),
                "end": ev.end.isoformat(),
                "join_url": ev.join_url,
            },
            status=DetectedEvent.Status.PUBLISHED,
        )
        emit(
            "calendar.event",
            "ears",
            payload={
                "detection_id": det_id,
                "calendar_id": calendar_id,
                "event": ev.title,
                "start": ev.start.isoformat(),
            },
        )
        if ev.join_url or "meet" in ev.title.lower() or "teams" in (ev.join_url or "").lower():
            emit(
                "meeting.detected",
                "ears",
                payload={
                    "detection_id": det_id,
                    "provider": "outlook" if "teams" in (ev.join_url or "") else "google_meet",
                    "meeting_id": ev.external_id,
                    "title": ev.title,
                    "join_url": ev.join_url,
                },
            )

    def verify_webhook(self, listener_name: str, headers: dict[str, str], body: bytes) -> bool:
        listener = Listener.objects.filter(name=listener_name).first()
        if not listener:
            return False
        secret = listener.config.get("webhook_secret") or self._dna.webhook_secret
        adapter: WebhookPort
        if listener.kind == Listener.Kind.GOOGLE_CALENDAR:
            from .adapters.google_calendar_adapter import GoogleCalendarAdapter

            adapter = GoogleCalendarAdapter()
        else:
            from .adapters.outlook_adapter import OutlookCalendarAdapter

            adapter = OutlookCalendarAdapter()
        return adapter.verify(headers, body, str(secret))


_service: EarsService | None = None


def get_ears_service() -> EarsService:
    global _service
    if _service is None:
        _service = EarsService()
    return _service
