"""
Skeleton Ports — Project scaffolding and template application.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScaffoldRequest:
    """Input for creating or updating project structure."""

    project_slug: str
    template_key: str | None
    target_root: Path
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScaffoldResult:
    success: bool
    message: str = ""
    created_paths: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StructureReport:
    valid: bool
    missing: list[str] = field(default_factory=list)
    unexpected: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class ProjectPort(ABC):
    """Port for filesystem project operations."""

    @abstractmethod
    def scaffold(self, request: ScaffoldRequest) -> ScaffoldResult:
        """Create directories and seed files from a template."""

    @abstractmethod
    def validate_structure(self, project_root: Path, expected_layout: dict[str, Any]) -> StructureReport:
        """Verify required paths exist relative to project root."""


@dataclass
class TemplateDescriptor:
    key: str
    label: str
    version: int
    path: Path


class TemplatePort(ABC):
    """Port for discovering and rendering templates."""

    @abstractmethod
    def list_templates(self) -> list[TemplateDescriptor]:
        """Return installable templates."""

    @abstractmethod
    def apply(self, template_key: str, target: Path, variables: dict[str, Any]) -> ScaffoldResult:
        """Copy/render a template into target."""
