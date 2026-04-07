"""
Memory ports — Vector store and high-level knowledge operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VectorRecord:
    """Single stored vector with optional metadata."""

    id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    document: str = ""


@dataclass
class SearchResult:
    """One hit from similarity search."""

    id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    document: str = ""


class VectorStorePort(ABC):
    """Low-level vector database operations."""

    @abstractmethod
    def store(self, collection: str, records: list[VectorRecord]) -> list[str]:
        """Persist records; returns stored ids."""

    @abstractmethod
    def search(
        self, collection: str, query_vector: list[float], limit: int
    ) -> list[SearchResult]:
        """Similarity search in a collection."""

    @abstractmethod
    def delete(self, collection: str, ids: list[str]) -> int:
        """Remove ids; returns count removed."""

    @abstractmethod
    def list_collections(self) -> list[str]:
        """Names of all collections visible to this backend."""


class KnowledgePort(ABC):
    """Semantic knowledge API built on top of the vector store."""

    @abstractmethod
    def remember(self, text: str, collection: str, metadata: dict[str, Any] | None = None) -> str:
        """Embed and store text; returns knowledge entry id."""

    @abstractmethod
    def recall(self, query: str, collection: str | None, limit: int | None = None) -> list[SearchResult]:
        """Search by natural language query."""

    @abstractmethod
    def forget(self, entry_ids: list[str], collection: str | None = None) -> int:
        """Delete knowledge entries by id."""
