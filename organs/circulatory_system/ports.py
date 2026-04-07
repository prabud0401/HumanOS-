"""
Circulatory ports — Abstract transport interfaces.

Defines how data is routed, optionally transformed, and validated before delivery.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TransitEnvelope:
    """Wrapper for in-flight organ-to-organ payloads."""

    packet_id: str
    source_organ: str
    target_organ: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class TransportPort(ABC):
    """Port for moving data between organs."""

    @abstractmethod
    def route(self, envelope: TransitEnvelope) -> str:
        """
        Schedule or execute routing to ``target_organ``.

        Returns a delivery or job identifier.
        """

    @abstractmethod
    def transform_in_transit(
        self, payload: dict[str, Any], transforms: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply a list of transform specs (e.g. redact, compress ref, map fields).

        Implementations must be deterministic where possible.
        """

    @abstractmethod
    def validate_delivery(self, envelope: TransitEnvelope, receipt_token: str) -> bool:
        """Verify integrity / authorization of a completed delivery."""
