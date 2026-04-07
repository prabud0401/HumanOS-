"""
Reproductive models — clones, config snapshots, migration audit.
"""

from django.db import models


class CloneInstance(models.Model):
    """Registered clone of this twin."""

    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "Provisioning"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        DECOMMISSIONED = "decommissioned", "Decommissioned"

    clone_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    template_version = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PROVISIONING)
    path = models.CharField(max_length=512, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"CloneInstance({self.clone_id})"


class CloneConfig(models.Model):
    """Snapshot of DNA / settings used for a clone."""

    config_id = models.CharField(max_length=128, unique=True)
    clone = models.ForeignKey(
        CloneInstance, on_delete=models.CASCADE, related_name="configs", null=True, blank=True
    )
    payload = models.JSONField(default=dict)
    checksum = models.CharField(max_length=128, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"CloneConfig({self.config_id})"


class MigrationLog(models.Model):
    """Audit entry for migrate / rollback."""

    class Direction(models.TextChoices):
        UP = "up", "Up"
        DOWN = "down", "Down"

    plan_id = models.CharField(max_length=128, db_index=True)
    direction = models.CharField(max_length=8, choices=Direction.choices)
    success = models.BooleanField(default=False)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"MigrationLog({self.plan_id}, {self.direction})"
