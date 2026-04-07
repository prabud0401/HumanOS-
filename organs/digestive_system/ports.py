"""
Digestive System Ports — Parsing and transformation pipelines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParseResult:
    format: str
    text: str
    segments: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ParserPort(ABC):
    @abstractmethod
    def parse_vtt(self, path: Path | str) -> ParseResult:
        """Parse WebVTT (or SRT) captions/transcript."""

    @abstractmethod
    def parse_pdf(self, path: Path | str) -> ParseResult:
        """Extract text (and optional structure) from PDF."""

    @abstractmethod
    def parse_email(self, path: Path | str) -> ParseResult:
        """Parse .eml or RFC822 content."""


@dataclass
class TransformResult:
    data: dict[str, Any]
    valid: bool
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TransformPort(ABC):
    @abstractmethod
    def transform(self, data: dict[str, Any], ruleset: str | None = None) -> TransformResult:
        """Apply transformation rules to structured data."""

    @abstractmethod
    def validate(self, data: dict[str, Any], schema: dict[str, Any]) -> TransformResult:
        """Validate against a JSON-schema-like dict (lightweight)."""

    @abstractmethod
    def enrich(self, data: dict[str, Any], context: dict[str, Any]) -> TransformResult:
        """Enrich with NLP or external lookups."""
