"""
Voice organ models — channels, templates, and delivery log.
"""

from django.db import models


class Channel(models.Model):
    """An outbound destination (Slack workspace, SMTP profile, Teams webhook)."""

    class Kind(models.TextChoices):
        SLACK = "slack", "Slack"
        EMAIL = "email", "Email"
        TEAMS_CHAT = "teams_chat", "Teams Chat"

    slug = models.SlugField(max_length=64, unique=True)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="webhook URL, bot token, SMTP host, etc. (never log secrets)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return f"Channel({self.slug})"


class NotificationTemplate(models.Model):
    """Reusable message shapes per channel."""

    name = models.CharField(max_length=128, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="templates")
    subject = models.CharField(max_length=256, blank=True, default="")
    body = models.TextField(help_text="May contain {placeholders} filled from payload")
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"NotificationTemplate({self.name})"


class Notification(models.Model):
    """Audit row for a single send attempt."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    notification_id = models.CharField(max_length=64, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True, related_name="notifications")
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    event_type = models.CharField(max_length=128, blank=True, default="", db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    rendered_subject = models.CharField(max_length=512, blank=True, default="")
    rendered_body = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification({self.notification_id}: {self.status})"
