"""
Memory organ models — knowledge entries, collections, search audit log.
"""

from django.db import models


class Collection(models.Model):
    """Logical vector collection (maps to backend namespace)."""

    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, default="")
    embedding_model = models.CharField(max_length=128, default="")
    record_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]
        verbose_name_plural = "collections"

    def __str__(self) -> str:
        return f"Collection({self.slug})"


class KnowledgeEntry(models.Model):
    """Metadata for a stored knowledge chunk (vector lives in external store)."""

    entry_id = models.CharField(max_length=128, unique=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="entries")
    title = models.CharField(max_length=512, blank=True, default="")
    source_organ = models.CharField(max_length=64, blank=True, default="")
    source_event_id = models.CharField(max_length=128, blank=True, default="")
    content_preview = models.TextField(blank=True, default="")
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"KnowledgeEntry({self.entry_id})"


class SearchLog(models.Model):
    """Audit trail for recall / search operations."""

    query_text = models.TextField()
    collection = models.ForeignKey(
        Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name="search_logs"
    )
    result_count = models.PositiveIntegerField(default=0)
    top_score = models.FloatField(null=True, blank=True)
    latency_ms = models.FloatField(default=0.0)
    requested_by = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"SearchLog({self.pk}, n={self.result_count})"
