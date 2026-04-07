"""
Brain Ports — Abstract interfaces for AI capabilities.

These define WHAT the brain can do, not HOW it does it.
Concrete adapters implement these for each LLM provider.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMRequest:
    """Standard request to any LLM adapter."""
    prompt: str
    system_prompt: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096
    model: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Standard response from any LLM adapter."""
    content: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


class LLMPort(ABC):
    """Port for interacting with Large Language Models."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion from the LLM."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is reachable."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier."""


@dataclass
class EmbeddingRequest:
    text: str
    model: str | None = None


@dataclass
class EmbeddingResponse:
    vector: list[float]
    model: str
    dimensions: int


class EmbeddingPort(ABC):
    """Port for generating text embeddings."""

    @abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate an embedding vector for the input text."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Generate embeddings for multiple texts."""


class DecisionPort(ABC):
    """Port for the decision-making pipeline."""

    @abstractmethod
    def analyze(self, context: str, knowledge: list[str]) -> dict[str, Any]:
        """Analyze context and relevant knowledge, return structured analysis."""

    @abstractmethod
    def decide(self, analysis: dict, constraints: dict | None = None) -> dict[str, Any]:
        """Make a decision based on analysis. Returns action + reasoning."""

    @abstractmethod
    def explain(self, decision: dict) -> str:
        """Generate a human-readable explanation of a decision."""
