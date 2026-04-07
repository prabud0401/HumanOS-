"""
Hands organ models — tasks, execution audit trail, and discrete agent actions.
"""

from django.db import models


class Task(models.Model):
    """A unit of work the Hands organ may execute (from Brain or scheduler)."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    task_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, default="")
    action_type = models.CharField(
        max_length=64,
        help_text="Logical action key, e.g. shell.run, github.pr.create",
    )
    payload = models.JSONField(default=dict, help_text="Structured parameters for adapters")
    priority = models.PositiveSmallIntegerField(default=5)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    source_event_id = models.CharField(max_length=128, blank=True, default="")
    decision_ref = models.CharField(max_length=128, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Task({self.task_id}: {self.status})"


class TaskExecution(models.Model):
    """Immutable-style log of each attempt to run a task (supports retries)."""

    class Outcome(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"
        ROLLED_BACK = "rolled_back", "Rolled Back"
        SKIPPED = "skipped", "Skipped"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="executions")
    execution_id = models.CharField(max_length=64, unique=True)
    adapter = models.CharField(max_length=64, help_text="Adapter that performed the work")
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    stdout = models.TextField(blank=True, default="")
    stderr = models.TextField(blank=True, default="")
    exit_code = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    duration_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TaskExecution({self.execution_id}: {self.outcome})"


class AgentAction(models.Model):
    """A delegated sub-action performed by or on behalf of an external agent."""

    class State(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        ERROR = "error", "Error"

    action_id = models.CharField(max_length=64, unique=True)
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_actions",
    )
    agent_name = models.CharField(max_length=128)
    capability = models.CharField(max_length=128, help_text="What the agent was asked to do")
    input_snapshot = models.JSONField(default=dict)
    output_snapshot = models.JSONField(default=dict)
    state = models.CharField(max_length=16, choices=State.choices, default=State.PENDING)
    correlation_id = models.CharField(max_length=128, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AgentAction({self.action_id}: {self.state})"
