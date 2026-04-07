"""
Digestive System models — jobs, extracted knowledge, and transformation rules.
"""

from django.db import models


class ProcessingJob(models.Model):
    """A single run through the ingestion / transform pipeline."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    job_id = models.CharField(max_length=64, unique=True)
    source_uri = models.CharField(max_length=1024, help_text="Path, URL, or blob reference")
    format = models.CharField(max_length=32, help_text="vtt, srt, pdf, eml, ...")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, default="")
    stats = models.JSONField(default=dict, help_text="Counts, timings, adapter metadata")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ProcessingJob({self.job_id}: {self.status})"


class ExtractedKnowledge(models.Model):
    """Structured facts or chunks extracted from raw content."""

    class Kind(models.TextChoices):
        ENTITY = "entity", "Entity"
        FACT = "fact", "Fact"
        SUMMARY = "summary", "Summary"
        TRANSCRIPT_CHUNK = "transcript_chunk", "Transcript Chunk"

    knowledge_id = models.CharField(max_length=64, unique=True)
    job = models.ForeignKey(
        ProcessingJob,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="knowledge_items",
    )
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.FACT)
    title = models.CharField(max_length=512, blank=True, default="")
    content = models.TextField()
    confidence = models.FloatField(default=1.0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Extracted knowledge"

    def __str__(self):
        return f"ExtractedKnowledge({self.knowledge_id})"


class TransformationRule(models.Model):
    """Named rule applied during transform/enrich stages."""

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, default="")
    rule_type = models.CharField(max_length=64, help_text="map, filter, enrich, validate")
    config = models.JSONField(default=dict)
    priority = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "name"]

    def __str__(self):
        return f"TransformationRule({self.name})"
