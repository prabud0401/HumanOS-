"""
Eyes Ports — dashboard rendering and layout resolution.
"""

from abc import ABC, abstractmethod
from typing import Any


class DashboardPort(ABC):
    """Abstract surface for building dashboard payloads (HTML, JSON, or both)."""

    @abstractmethod
    def render_widget(self, slug: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return a serializable widget view model for the frontend."""

    @abstractmethod
    def get_layout(self, user_id: int | None = None) -> dict[str, Any]:
        """Resolve ordered widgets + theme for the given user (or anonymous defaults)."""
