"""
Nervous System models — signal definitions and connection registry.
"""

from django.db import models


class Signal(models.Model):
    """Logical signal type that may be broadcast to clients."""

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, default="")
    channel = models.CharField(max_length=128, db_index=True, help_text="Routing channel, e.g. organ.brain")
    schema = models.JSONField(default=dict, help_text="Optional JSON schema for payload validation")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Signal({self.name})"


class Connection(models.Model):
    """Persisted metadata for an active real-time client (WS/SSE)."""

    class Transport(models.TextChoices):
        WEBSOCKET = "websocket", "WebSocket"
        SSE = "sse", "Server-Sent Events"

    class State(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    connection_id = models.CharField(max_length=64, unique=True)
    transport = models.CharField(max_length=16, choices=Transport.choices)
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    subscribed_channels = models.JSONField(default=list)
    state = models.CharField(max_length=16, choices=State.choices, default=State.OPEN)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"Connection({self.connection_id}, {self.transport})"
