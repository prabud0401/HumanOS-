"""
Ears organ models — listener configuration and detected signals.
"""

from django.db import models


class Listener(models.Model):
    """A configured inbound channel (calendar, webhook, mailbox)."""

    class Kind(models.TextChoices):
        OUTLOOK_CALENDAR = "outlook_calendar", "Outlook Calendar"
        GOOGLE_CALENDAR = "google_calendar", "Google Calendar"
        WEBHOOK_GENERIC = "webhook_generic", "Generic Webhook"
        TEAMS_SUBSCRIPTION = "teams_subscription", "Teams Subscription"

    name = models.CharField(max_length=128, unique=True)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific: calendar id, resource URL, filters",
    )
    last_poll_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Listener({self.name})"


class DetectedEvent(models.Model):
    """Something the Ears organ observed and may have published to the bus."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        PUBLISHED = "published", "Published"
        IGNORED = "ignored", "Ignored"
        ERROR = "error", "Error"

    detection_id = models.CharField(max_length=64, unique=True)
    listener = models.ForeignKey(
        Listener,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detections",
    )
    signal_type = models.CharField(max_length=64, db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    normalized_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    bus_event_id = models.CharField(max_length=128, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"DetectedEvent({self.signal_type}:{self.detection_id})"
