"""
Brain DNA — Reads organ-specific configuration from identity.yaml.

The brain's DNA determines which LLM to use, temperature settings,
context window size, and reasoning preferences.
"""

from dataclasses import dataclass
from core.dna_loader import get_dna


@dataclass
class BrainDNA:
    primary_model: str
    fallback_model: str
    adapter: str
    temperature: float
    max_context_tokens: int
    embedding_model: str
    vector_db: str


def get_brain_dna() -> BrainDNA:
    """Extract brain-specific config from the global DNA."""
    dna = get_dna()
    ai = dna.ai_engine
    return BrainDNA(
        primary_model=ai.primary_model,
        fallback_model=ai.fallback_model,
        adapter=ai.adapter,
        temperature=ai.temperature,
        max_context_tokens=ai.max_context_tokens,
        embedding_model=ai.embedding_model,
        vector_db=ai.vector_db,
    )
