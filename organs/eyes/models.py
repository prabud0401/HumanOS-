"""
Eyes organ models — dashboard widgets and user-facing preferences.
"""

from django.conf import settings
from django.db import models


class DashboardWidget(models.Model):
    """A tile, chart, or panel on the operator dashboard."""

    class WidgetType(models.TextChoices):
        KPI = "kpi", "KPI"
        TIMELINE = "timeline", "Timeline"
        TASKS = "tasks", "Tasks"
        MEETINGS = "meetings", "Meetings"
        CUSTOM = "custom", "Custom"

    slug = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=128)
    widget_type = models.CharField(max_length=32, choices=WidgetType.choices, default=WidgetType.CUSTOM)
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data source keys, refresh hints, chart options",
    )
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "slug"]

    def __str__(self):
        return f"DashboardWidget({self.slug})"


class UserPreference(models.Model):
    """Per-user dashboard and UI preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eyes_preferences",
    )
    theme = models.CharField(max_length=32, default="system")
    layout_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserPreference({self.user_id})"
