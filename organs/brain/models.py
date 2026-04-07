"""
Brain organ models — tracks AI decisions, reasoning chains, and prompt history.
"""

from django.db import models


class Decision(models.Model):
    """A decision made by the AI engine."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXECUTED = "executed", "Executed"

    decision_id = models.CharField(max_length=64, unique=True)
    context = models.TextField(help_text="What triggered this decision")
    reasoning = models.TextField(help_text="Chain-of-thought reasoning")
    action = models.TextField(help_text="The decided action")
    confidence = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    source_event_id = models.CharField(max_length=128, blank=True, default="")
    model_used = models.CharField(max_length=64, default="")
    tokens_used = models.IntegerField(default=0)
    latency_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Decision({self.decision_id}: {self.status})"


class PromptTemplate(models.Model):
    """Reusable prompt templates for different reasoning tasks."""

    name = models.CharField(max_length=128, unique=True)
    template = models.TextField(help_text="Jinja2-style template with {{variables}}")
    category = models.CharField(max_length=64, default="general")
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"Prompt({self.name} v{self.version})"


class ReasoningChain(models.Model):
    """Tracks multi-step reasoning for complex decisions."""

    decision = models.ForeignKey(Decision, on_delete=models.CASCADE, related_name="chain_steps")
    step_number = models.IntegerField()
    input_text = models.TextField()
    output_text = models.TextField()
    model_used = models.CharField(max_length=64)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["decision", "step_number"]
        unique_together = ["decision", "step_number"]

    def __str__(self):
        return f"Step {self.step_number} of {self.decision.decision_id}"
