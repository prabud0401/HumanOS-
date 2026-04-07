"""
Reproductive ports — Clone lifecycle and migration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CloneSpec:
    """Requested clone parameters."""

    name: str
    target_path: str
    branch: str = "main"
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationPlan:
    """Steps to apply or roll back."""

    plan_id: str
    steps: list[dict[str, Any]] = field(default_factory=list)


class ClonePort(ABC):
    """Create and validate new instances from a template."""

    @abstractmethod
    def create_clone(self, spec: CloneSpec) -> str:
        """Materialize a clone; returns clone instance id."""

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """Return (ok, error messages)."""

    @abstractmethod
    def export_template(self, output_path: str) -> str:
        """Write template bundle; returns path or archive id."""


class MigrationPort(ABC):
    """Schema / config migrations between twin versions."""

    @abstractmethod
    def migrate(self, plan: MigrationPlan) -> dict[str, Any]:
        """Apply migration plan; returns status details."""

    @abstractmethod
    def rollback(self, plan: MigrationPlan) -> dict[str, Any]:
        """Reverse a plan when possible."""
