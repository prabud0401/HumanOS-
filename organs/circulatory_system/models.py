"""
Circulatory system models — pipelines, runs, and in-transit packets.
"""

import uuid

from django.db import models


class Pipeline(models.Model):
    """Declarative data pipeline between organs."""

    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, default="")
    source_organ = models.CharField(max_length=64)
    target_organ = models.CharField(max_length=64)
    transform_chain = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"Pipeline({self.slug})"


class PipelineRun(models.Model):
    """Single execution of a pipeline."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    run_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    trigger_event_id = models.CharField(max_length=128, blank=True, default="")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    stats = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"PipelineRun({self.run_id}, {self.status})"


class DataPacket(models.Model):
    """In-transit payload record (logical packet, may map to blob storage)."""

    class State(models.TextChoices):
        QUEUED = "queued", "Queued"
        IN_FLIGHT = "in_flight", "In flight"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    packet_id = models.CharField(max_length=128, unique=True)
    pipeline_run = models.ForeignKey(
        PipelineRun, on_delete=models.CASCADE, related_name="packets", null=True, blank=True
    )
    payload_ref = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="Storage key or inline reference for large payloads",
    )
    payload_summary = models.JSONField(default=dict, blank=True)
    state = models.CharField(max_length=16, choices=State.choices, default=State.QUEUED)
    byte_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"DataPacket({self.packet_id}, {self.state})"
