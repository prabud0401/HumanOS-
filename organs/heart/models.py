"""
Heart organ models — event audit trail and system heartbeats.
"""

from django.db import models


class EventLog(models.Model):
    """Persisted copy of events that flowed through the circulatory bus."""

    event_id = models.CharField(max_length=128, db_index=True)
    event_type = models.CharField(max_length=256, db_index=True)
    source_organ = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    received_at = models.DateTimeField(auto_now_add=True)
    routing_meta = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional bus metadata: stream id, consumer group, etc.",
    )

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["event_type", "-received_at"]),
            models.Index(fields=["source_organ", "-received_at"]),
        ]

    def __str__(self):
        return f"EventLog({self.event_type}@{self.event_id})"


class HeartbeatRecord(models.Model):
    """Periodic pulse emitted by the Heart to prove the bus is alive."""

    class Status(models.TextChoices):
        OK = "ok", "OK"
        DEGRADED = "degraded", "Degraded"
        FAILED = "failed", "Failed"

    beat_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OK)
    stream_name = models.CharField(max_length=256, default="")
    pending_events_estimate = models.IntegerField(default=0)
    subscribers_wildcard = models.IntegerField(
        default=0, help_text="Handlers registered on '*' at sample time"
    )
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Heartbeat({self.beat_id}: {self.status})"
