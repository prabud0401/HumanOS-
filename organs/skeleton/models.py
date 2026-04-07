"""
Skeleton organ models — projects, templates, and config entries.
"""

from django.db import models


class Project(models.Model):
    """A filesystem or logical project tracked by HumanOS."""

    class Kind(models.TextChoices):
        APP = "app", "Application"
        LIBRARY = "library", "Library"
        MONOREPO = "monorepo", "Monorepo"
        TOOLING = "tooling", "Tooling"

    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    root_path = models.CharField(max_length=512, help_text="Absolute or workspace-relative root")
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.APP)
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return f"Project({self.slug})"


class ProjectTemplate(models.Model):
    """Named template used to scaffold new projects or modules."""

    key = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=256)
    description = models.TextField(blank=True, default="")
    source_path = models.CharField(max_length=512, help_text="Directory containing template files")
    variables_schema = models.JSONField(
        default=dict,
        help_text="JSON schema or list of expected template variables",
    )
    version = models.PositiveIntegerField(default=1)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"ProjectTemplate({self.key}@{self.version})"


class ConfigEntry(models.Model):
    """Key/value configuration scoped to a project or global."""

    class Scope(models.TextChoices):
        GLOBAL = "global", "Global"
        PROJECT = "project", "Project"

    scope = models.CharField(max_length=16, choices=Scope.choices, default=Scope.GLOBAL)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="config_entries",
    )
    key = models.CharField(max_length=256, db_index=True)
    value = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scope", "key"]
        indexes = [
            models.Index(fields=["scope", "key"]),
        ]

    def __str__(self):
        return f"ConfigEntry({self.scope}:{self.key})"
