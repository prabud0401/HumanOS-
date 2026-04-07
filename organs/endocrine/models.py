"""
Endocrine models — schedules, jobs, reminders, timers.
"""

from django.db import models


class Schedule(models.Model):
    """Cron-style schedule template."""

    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    cron_expression = models.CharField(max_length=128, help_text="e.g. 0 9 * * *")
    timezone = models.CharField(max_length=64, default="UTC")
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"Schedule({self.slug})"


class ScheduledJob(models.Model):
    """Concrete scheduled execution record."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    external_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    schedule = models.ForeignKey(
        Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs"
    )
    name = models.CharField(max_length=256)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    payload = models.JSONField(default=dict, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ScheduledJob({self.name}, {self.status})"


class Reminder(models.Model):
    """User or system reminder at a specific time."""

    title = models.CharField(max_length=512)
    fire_at = models.DateTimeField()
    timezone = models.CharField(max_length=64, default="UTC")
    delivered = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fire_at"]

    def __str__(self) -> str:
        return f"Reminder({self.title})"


class Timer(models.Model):
    """Persisted timer for audit / recovery (ephemeral timers also exist in adapters)."""

    timer_id = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=256, blank=True, default="")
    fire_at = models.DateTimeField()
    cancelled = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fire_at"]

    def __str__(self) -> str:
        return f"Timer({self.timer_id})"
