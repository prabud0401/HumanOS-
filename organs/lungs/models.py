"""
Lungs organ models — ingestion jobs and stored artifacts.
"""

from django.db import models


class IngestionJob(models.Model):
    """Tracks a single download / sync run (e.g., one meeting or one batch)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Source(models.TextChoices):
        TEAMS = "teams", "Microsoft Teams"
        ZOOM = "zoom", "Zoom"
        GOOGLE_MEET = "google_meet", "Google Meet"
        OTHER = "other", "Other"

    job_id = models.CharField(max_length=64, unique=True)
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.OTHER)
    external_ref = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="Provider meeting id, drive file id, etc.",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"IngestionJob({self.job_id}: {self.status})"


class Artifact(models.Model):
    """A file or blob produced by ingestion (recording, transcript, attachment)."""

    class Kind(models.TextChoices):
        RECORDING = "recording", "Recording"
        TRANSCRIPT = "transcript", "Transcript"
        CHAT = "chat", "Chat Log"
        FILE = "file", "Generic File"
        OTHER = "other", "Other"

    artifact_id = models.CharField(max_length=64, unique=True)
    job = models.ForeignKey(
        IngestionJob,
        on_delete=models.CASCADE,
        related_name="artifacts",
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.FILE)
    logical_name = models.CharField(max_length=512)
    storage_path = models.CharField(max_length=1024, help_text="Local or blob URI")
    content_type = models.CharField(max_length=128, blank=True, default="")
    byte_size = models.BigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Artifact({self.logical_name})"
