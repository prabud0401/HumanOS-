"""
Immune System models — incidents, policies, audit trail, and keys.
"""

from django.db import models


class SecurityEvent(models.Model):
    """A detected threat or security-relevant incident."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        QUARANTINED = "quarantined", "Quarantined"
        RESOLVED = "resolved", "Resolved"

    event_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, default="")
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    source_event_id = models.CharField(max_length=128, blank=True, default="")
    context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SecurityEvent({self.event_id}: {self.severity})"


class AccessPolicy(models.Model):
    """Declarative rule evaluated by the authorization pipeline."""

    name = models.CharField(max_length=128, unique=True)
    resource_pattern = models.CharField(max_length=256, help_text="Glob or regex key for resource")
    actions = models.JSONField(default=list, help_text="Allowed actions, e.g. read, write, execute")
    roles = models.JSONField(default=list, help_text="Roles or principals allowed")
    priority = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "name"]

    def __str__(self):
        return f"AccessPolicy({self.name})"


class AuditLog(models.Model):
    """Immutable audit record for auth decisions and sensitive operations."""

    log_id = models.CharField(max_length=64, unique=True)
    actor = models.CharField(max_length=256, blank=True, default="")
    action = models.CharField(max_length=128)
    resource = models.CharField(max_length=512)
    allowed = models.BooleanField()
    reason = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AuditLog({self.log_id}: {self.action})"


class EncryptionKey(models.Model):
    """Logical encryption key material (references KMS/secret store in production)."""

    class State(models.TextChoices):
        ACTIVE = "active", "Active"
        ROTATING = "rotating", "Rotating"
        RETIRED = "retired", "Retired"

    key_id = models.CharField(max_length=128, unique=True)
    algorithm = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)
    state = models.CharField(max_length=16, choices=State.choices, default=State.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    retired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"EncryptionKey({self.key_id} v{self.version})"
